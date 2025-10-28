import os
from typing import List, Optional, Dict, Any
from openai import OpenAI
from app.schemas.chat_enhanced import ChatMessage
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log_file import LogFile
from sqlalchemy import select
import logging
from datetime import datetime
from app.services.llm.llm_service import UnifiedLLMService, LLMRequest, LLMTask
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

class EnhancedChatService:
    def __init__(self):
        # Initialize OpenAI client (works with OpenRouter and other OpenAI-compatible APIs)
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY", "your-openrouter-api-key"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct")
        
        # Cost tracking headers for OpenRouter
        self.extra_headers = {
            "HTTP-Referer": "https://loglytics-ai.com",  # Your app domain
            "X-Title": "Loglytics AI"  # Your app name
        }
    
    async def get_log_content(self, file_id: str, db: AsyncSession) -> Optional[str]:
        """Retrieve log file content from database"""
        result = await db.execute(
            select(LogFile).where(LogFile.id == file_id)
        )
        log_file = result.scalar_one_or_none()
        
        if not log_file:
            return None
        
        # Read file content from S3 or local storage
        try:
            if log_file.s3_key:
                # If using S3, you'd need to implement S3 download here
                # For now, we'll assume local file storage
                return "File content from S3 (implement S3 download)"
            else:
                # Local file storage
                file_path = f"uploads/{log_file.filename}"
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Limit content size (first 10000 chars for context)
                    if len(content) > 10000:
                        content = content[:10000] + "\n... (truncated for length)"
                    
                    return content
                else:
                    return None
        except Exception as e:
            print(f"Error reading log file: {e}")
            return None
    
    async def chat(
        self,
        message: str,
        conversation_history: List[ChatMessage],
        conversation_id: Optional[str] = None,
        file_id: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        db: Optional[AsyncSession] = None,
        user: Optional[UserResponse] = None  # Added user parameter for subscription check
    ) -> str:
        """Send message to AI with RAG context"""
        
        # Build messages for the API
        messages = []
        
        # System prompt
        system_prompt = """You are an expert AI assistant specializing in log analysis and troubleshooting. 
You help developers understand their application logs, detect patterns, identify errors, and provide actionable insights.

When analyzing logs:
- Identify error patterns and root causes
- Explain technical issues in clear language
- Suggest solutions and best practices
- Highlight critical issues that need immediate attention
- Provide context about common errors and how to fix them

Be concise, helpful, and actionable in your responses."""
        
        # Add RAG context if available
        rag_context = ""
        
        # Search conversation history using RAG if conversation_id is provided
        if conversation_id and user_id and project_id:
            try:
                from app.services.rag.rag_service import RAGService
                from app.schemas.user import UserResponse
                
                # Create a mock user object for RAG service
                mock_user = UserResponse(
                    id=user_id,
                    email="user@example.com",
                    full_name="User",
                    subscription_tier="free",
                    selected_llm_model="local",
                    is_active=True,
                    created_at=datetime.now()
                )
                
                # Initialize RAG service
                rag_service = RAGService(db)
                await rag_service.initialize()
                
                # Search for relevant context from conversation history
                conv_context = await rag_service.search_similar_content(
                    content=message,
                    project_id=project_id,
                    user_id=user_id,
                    limit=3
                )
                
                if conv_context:
                    rag_context += "\n\n**Previous conversation context:**\n"
                    for ctx in conv_context[:2]:  # Limit to 2 most relevant
                        rag_context += f"- {ctx.get('content', '')[:200]}...\n"
                
                # Search log files using RAG
                log_context = await rag_service.search_similar_content(
                    content=message,
                    project_id=project_id,
                    user_id=user_id,
                    limit=3
                )
                
                if log_context:
                    rag_context += "\n\n**Relevant log excerpts:**\n"
                    for ctx in log_context[:2]:  # Limit to 2 most relevant
                        rag_context += f"```\n{ctx.get('content', '')[:300]}...\n```\n"
                
                logger.info(f"RAG context added: {len(rag_context)} characters")
                
            except Exception as e:
                logger.error(f"Error getting RAG context: {e}")
                # Continue without RAG context if there's an error
        
        # Add log file content if provided
        if file_id and db:
            log_content = await self.get_log_content(file_id, db)
            if log_content:
                messages.append({
                    "role": "system",
                    "content": f"Current log file being analyzed:\n\n```\n{log_content}\n```"
                })
        
        # Add RAG context to system prompt
        if rag_context:
            system_prompt += f"\n\n{rag_context}"
        
        messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (last 5 messages)
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": message
        })
        
        try:
            # Call OpenRouter API with cost tracking headers
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                extra_headers=self.extra_headers
            )
            
            # Log usage for cost tracking
            if hasattr(response, 'usage'):
                logger.info(f"OpenRouter API Usage - Model: {response.model}")
                logger.info(f"Input tokens: {response.usage.prompt_tokens}")
                logger.info(f"Output tokens: {response.usage.completion_tokens}")
                logger.info(f"Total tokens: {response.usage.total_tokens}")
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error calling AI API: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

# Create singleton instance
enhanced_chat_service = EnhancedChatService()

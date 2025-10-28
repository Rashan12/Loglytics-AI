"""
Unified Chat Service for Loglytics AI
Uses the unified LLM service to handle both local and cloud models based on user subscription
"""

import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat_enhanced import ChatMessage
from app.schemas.user import UserResponse
from app.models.log_file import LogFile
from sqlalchemy import select
from datetime import datetime
from app.services.llm.llm_service import UnifiedLLMService, LLMRequest, LLMTask

logger = logging.getLogger(__name__)

class UnifiedChatService:
    """Unified chat service that uses the unified LLM service"""
    
    def __init__(self):
        self.service_name = "UnifiedChatService"
        logger.info("Initialized Unified Chat Service")
    
    async def get_log_content(self, file_id: str, db: AsyncSession) -> Optional[str]:
        """Retrieve log file content from database"""
        try:
            result = await db.execute(
                select(LogFile).where(LogFile.id == file_id)
            )
            log_file = result.scalar_one_or_none()
            
            if not log_file:
                return None
            
            # Read file content from local storage
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
            logger.error(f"Error reading log file: {e}")
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
        user: Optional[UserResponse] = None
    ) -> str:
        """Send message to AI with RAG context using unified LLM service"""
        
        try:
            # Create a mock user if not provided
            if not user:
                user = UserResponse(
                    id=user_id or "default",
                    email="user@example.com",
                    full_name="User",
                    subscription_tier="free",
                    selected_llm_model="local",
                    is_active=True,
                    created_at=datetime.now()
                )
            
            # Initialize unified LLM service
            llm_service = UnifiedLLMService(db)
            
            # Build context for the request
            context = {}
            
            # RAG context disabled due to missing pgvector extension
            # if conversation_id and user_id and project_id:
            #     try:
            #         from app.services.rag.rag_service import RAGService
            #         
            #         # Initialize RAG service
            #         rag_service = RAGService(db)
            #         await rag_service.initialize()
            #         
            #         # Search for relevant context from conversation history
            #         conv_context = await rag_service.search_similar_content(
            #             content=message,
            #             project_id=project_id,
            #             user_id=user_id,
            #             limit=3
            #         )
            #         
            #         if conv_context:
            #             context["conversation_context"] = conv_context[:2]
            #             logger.info(f"RAG conversation context added: {len(conv_context)} items")
            #         
            #         # Search log files using RAG
            #         log_context = await rag_service.search_similar_content(
            #             content=message,
            #             project_id=project_id,
            #             user_id=user_id,
            #             limit=3
            #         )
            #         
            #         if log_context:
            #             context["log_context"] = log_context[:2]
            #             logger.info(f"RAG log context added: {len(log_context)} items")
            #         
            #     except Exception as e:
            #         logger.error(f"Error getting RAG context: {e}")
            #         # Continue without RAG context if there's an error
            
            # Add log file content if provided
            if file_id and db:
                log_content = await self.get_log_content(file_id, db)
                if log_content:
                    context["current_log_file"] = log_content
                    logger.info(f"Current log file content added: {len(log_content)} characters")
            
            # Convert conversation history to the format expected by LLM service
            conversation_history_dict = [
                {"role": msg.role, "content": msg.content}
                for msg in conversation_history[-5:]  # Last 5 messages
            ]
            
            # Call OpenRouter directly for chat - bypass system prompt wrapper
            logger.info(f"🎯 Calling OpenRouter directly for user: {user.subscription_tier}")
            
            from app.services.llm.openrouter_client import OpenRouterClient
            openrouter = OpenRouterClient()
            
            # Add conversation history
            messages = []
            if conversation_history_dict:
                messages.extend(conversation_history_dict[-5:])  # Last 5 messages
            
            # Add current message (it already has proper context)
            messages.append({"role": "user", "content": message})
            
            # Generate response
            response_content = await openrouter.generate_response(
                prompt=message,
                context=None,  # Context is already in the message
                conversation_history=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            
            logger.info(f"LLM Response - Model: {openrouter.model}")
            logger.info(f"Response length: {len(response_content)}")
            
            return response_content
        
        except Exception as e:
            logger.error(f"Error in unified LLM chat: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."

# Create singleton instance
unified_chat_service = UnifiedChatService()

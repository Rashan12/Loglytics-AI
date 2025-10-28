"""
OpenRouter Client for Loglytics AI
Handles Llama 4 Maverick model integration using OpenRouter API
"""

import os
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class OpenRouterClient:
    """Client for Llama 4 Maverick model via OpenRouter API"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        # Use the model from .env file (meta-llama/llama-3.2-90b-vision-instruct)
        self.model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.2-90b-vision-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        
        # Initialize OpenAI client for OpenRouter
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Cost tracking headers
        self.extra_headers = {
            "HTTP-Referer": "https://loglytics-ai.com",
            "X-Title": "Loglytics AI"
        }
    
    async def health_check(self) -> bool:
        """Check if OpenRouter API is available"""
        try:
            if not self.api_key or self.api_key == "your-openrouter-api-key-here":
                logger.error("OpenRouter API key not configured")
                logger.error("Please set OPENROUTER_API_KEY environment variable")
                return False
            
            logger.info(f"Testing OpenRouter API with model: {self.model}")
            
            # Test with a simple request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                extra_headers=self.extra_headers
            )
            
            logger.info("OpenRouter API health check passed")
            return True
        except Exception as e:
            logger.error(f"OpenRouter health check failed: {e}")
            logger.error("Please check your API key and internet connection")
            return False
    
    async def generate_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Generate response using OpenRouter API"""
        try:
            # Use the conversation_history if provided, otherwise build from prompt
            if conversation_history and len(conversation_history) > 0:
                messages = conversation_history
            else:
                # Build messages from scratch
                messages = []
                
                # Add system prompt if context provided
                if context:
                    system_prompt = self._build_system_prompt(context)
                    messages.append({"role": "system", "content": system_prompt})
                
                # Add current prompt
                messages.append({"role": "user", "content": prompt})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream,
                extra_headers=self.extra_headers
            )
            
            # Log usage for cost tracking
            if hasattr(response, 'usage'):
                logger.info(f"OpenRouter API Usage - Model: {response.model}")
                logger.info(f"Input tokens: {response.usage.prompt_tokens}")
                logger.info(f"Output tokens: {response.usage.completion_tokens}")
                logger.info(f"Total tokens: {response.usage.total_tokens}")
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    async def generate_streaming_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenRouter API"""
        try:
            # Build messages
            messages = []
            
            # Add system prompt if context provided
            if context:
                system_prompt = self._build_system_prompt(context)
                messages.append({"role": "system", "content": system_prompt})
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add current prompt
            messages.append({"role": "user", "content": prompt})
            
            # Make streaming API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                extra_headers=self.extra_headers
            )
            
            # Stream the response
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenRouter streaming API error: {e}")
            yield f"I apologize, but I encountered an error: {str(e)}"
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build system prompt from context"""
        system_prompt = """You are an expert AI assistant specializing in log analysis and troubleshooting. 
You help developers understand their application logs, detect patterns, identify errors, and provide actionable insights.

When analyzing logs:
- Identify error patterns and root causes
- Explain technical issues in clear language
- Suggest solutions and best practices
- Highlight critical issues that need immediate attention
- Provide context about common errors and how to fix them

Be concise, helpful, and actionable in your responses."""
        
        # Add context-specific information
        if context.get("log_type"):
            system_prompt += f"\n\nLog type: {context['log_type']}"
        
        if context.get("application"):
            system_prompt += f"\n\nApplication: {context['application']}"
        
        if context.get("environment"):
            system_prompt += f"\n\nEnvironment: {context['environment']}"
        
        return system_prompt
    
    def _handle_streaming_response(self, response) -> str:
        """Handle streaming response and return full content"""
        content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
        return content
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "OpenRouter",
            "model": self.model,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key and self.api_key != "your-openrouter-api-key-here")
        }

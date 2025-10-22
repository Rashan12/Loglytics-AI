"""
Unified LLM Service for Loglytics AI
Handles both local Ollama models and cloud-based Llama 4 Maverick model
"""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass
from enum import Enum
from sqlalchemy.orm import Session

from app.models.user import User, SubscriptionTier
from app.models.usage_tracking import UsageTracking
from app.schemas.user import UserResponse
from app.services.llm.ollama_client import OllamaClient
from app.services.llm.maverick_client import MaverickClient
from app.services.llm.prompt_templates import PromptTemplates
from app.services.llm.response_parser import ResponseParser
from app.config import settings

logger = logging.getLogger(__name__)

class LLMTask(str, Enum):
    """LLM task types"""
    CHAT = "chat"
    LOG_ANALYSIS = "log_analysis"
    ERROR_DETECTION = "error_detection"
    ROOT_CAUSE = "root_cause"
    ANOMALY_DETECTION = "anomaly_detection"
    NATURAL_QUERY = "natural_query"
    SUMMARIZATION = "summarization"

@dataclass
class LLMRequest:
    """LLM request structure"""
    task: LLMTask
    prompt: str
    context: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    stream: bool = False
    structured_output: bool = False

@dataclass
class LLMResponse:
    """LLM response structure"""
    content: str
    model_used: str
    tokens_used: int
    latency_ms: float
    confidence_score: float
    metadata: Dict[str, Any]
    structured_data: Optional[Dict[str, Any]] = None

@dataclass
class LLMUsage:
    """LLM usage tracking"""
    user_id: str
    model: str
    tokens_used: int
    task: str
    cost: float = 0.0

class UnifiedLLMService:
    """Unified LLM service that handles multiple model providers"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ollama_client = OllamaClient()
        self.maverick_client = MaverickClient()
        self.prompt_templates = PromptTemplates()
        self.response_parser = ResponseParser()
        
        # Model availability tracking
        self._model_availability = {
            "ollama": False,
            "maverick": False
        }
        
        # Initialize clients
        asyncio.create_task(self._initialize_clients())
    
    async def _initialize_clients(self):
        """Initialize all LLM clients"""
        try:
            # Check Ollama availability
            self._model_availability["ollama"] = await self.ollama_client.health_check()
            logger.info(f"Ollama availability: {self._model_availability['ollama']}")
            
            # Check Maverick availability
            self._model_availability["maverick"] = await self.maverick_client.health_check()
            logger.info(f"Maverick availability: {self._model_availability['maverick']}")
            
        except Exception as e:
            logger.error(f"Error initializing LLM clients: {e}")
    
    async def generate_response(
        self,
        request: LLMRequest,
        user: UserResponse,
        db: Session
    ) -> Union[LLMResponse, AsyncGenerator[LLMResponse, None]]:
        """
        Generate LLM response based on user's selected model
        
        Args:
            request: LLM request
            user: User making the request
            db: Database session
            
        Returns:
            LLM response or async generator for streaming
        """
        try:
            # Check rate limiting based on user tier
            if not await self._check_rate_limits(user, request.task, db):
                raise ValueError("Rate limit exceeded for user tier")
            
            # Select model based on user preference and availability
            model_provider = await self._select_model(user, request.task)
            
            # Prepare prompt with context
            full_prompt = await self._prepare_prompt(request, user)
            
            # Generate response
            if request.stream:
                return self._generate_streaming_response(
                    model_provider, full_prompt, request, user, db
                )
            else:
                return await self._generate_single_response(
                    model_provider, full_prompt, request, user, db
                )
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._create_error_response(str(e))
    
    async def _select_model(self, user: UserResponse, task: LLMTask) -> str:
        """Select appropriate model based on user tier and availability"""
        # Pro users can use Maverick if available
        if user.subscription_tier == SubscriptionTier.PRO and self._model_availability["maverick"]:
            return "maverick"
        
        # Free users and fallback to Ollama
        if self._model_availability["ollama"]:
            return "ollama"
        
        # If no models available, try Maverick as last resort
        if self._model_availability["maverick"]:
            return "maverick"
        
        raise ValueError("No LLM models available")
    
    async def _prepare_prompt(self, request: LLMRequest, user: UserResponse) -> str:
        """Prepare full prompt with system message and context"""
        # Get system prompt for task
        system_prompt = self.prompt_templates.get_system_prompt(request.task)
        
        # Add conversation history if provided
        conversation_context = ""
        if request.conversation_history:
            conversation_context = self.prompt_templates.format_conversation_history(
                request.conversation_history
            )
        
        # Add context if provided
        context_str = ""
        if request.context:
            context_str = self.prompt_templates.format_context(request.context)
        
        # Combine all parts
        full_prompt = f"{system_prompt}\n\n{conversation_context}\n{context_str}\n\nUser: {request.prompt}"
        
        # Truncate if too long (keep last 4000 characters for context)
        if len(full_prompt) > 4000:
            full_prompt = full_prompt[-4000:]
        
        return full_prompt
    
    async def _generate_single_response(
        self,
        model_provider: str,
        prompt: str,
        request: LLMRequest,
        user: UserResponse,
        db: Session
    ) -> LLMResponse:
        """Generate single response (non-streaming)"""
        start_time = time.time()
        
        try:
            if model_provider == "ollama":
                response = await self.ollama_client.generate(
                    prompt=prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    structured_output=request.structured_output
                )
            elif model_provider == "maverick":
                response = await self.maverick_client.generate(
                    prompt=prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                    structured_output=request.structured_output
                )
            else:
                raise ValueError(f"Unknown model provider: {model_provider}")
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Parse response
            parsed_response = self.response_parser.parse_response(
                response, request.task, request.structured_output
            )
            
            # Track usage
            await self._track_usage(
                user_id=str(user.id),
                model=model_provider,
                tokens_used=parsed_response.get("tokens_used", 0),
                task=request.task.value,
                db=db
            )
            
            return LLMResponse(
                content=parsed_response["content"],
                model_used=model_provider,
                tokens_used=parsed_response.get("tokens_used", 0),
                latency_ms=latency_ms,
                confidence_score=parsed_response.get("confidence_score", 0.8),
                metadata={
                    "task": request.task.value,
                    "temperature": request.temperature,
                    "structured_output": request.structured_output
                },
                structured_data=parsed_response.get("structured_data")
            )
            
        except Exception as e:
            logger.error(f"Error generating response with {model_provider}: {e}")
            return self._create_error_response(str(e))
    
    async def _generate_streaming_response(
        self,
        model_provider: str,
        prompt: str,
        request: LLMRequest,
        user: UserResponse,
        db: Session
    ) -> AsyncGenerator[LLMResponse, None]:
        """Generate streaming response"""
        start_time = time.time()
        total_tokens = 0
        content_buffer = ""
        
        try:
            if model_provider == "ollama":
                async for chunk in self.ollama_client.generate_stream(
                    prompt=prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    content_buffer += chunk.get("content", "")
                    total_tokens += chunk.get("tokens", 0)
                    
                    yield LLMResponse(
                        content=chunk.get("content", ""),
                        model_used=model_provider,
                        tokens_used=chunk.get("tokens", 0),
                        latency_ms=(time.time() - start_time) * 1000,
                        confidence_score=0.8,
                        metadata={"streaming": True, "task": request.task.value}
                    )
            
            elif model_provider == "maverick":
                async for chunk in self.maverick_client.generate_stream(
                    prompt=prompt,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    content_buffer += chunk.get("content", "")
                    total_tokens += chunk.get("tokens", 0)
                    
                    yield LLMResponse(
                        content=chunk.get("content", ""),
                        model_used=model_provider,
                        tokens_used=chunk.get("tokens", 0),
                        latency_ms=(time.time() - start_time) * 1000,
                        confidence_score=0.8,
                        metadata={"streaming": True, "task": request.task.value}
                    )
            
            # Track final usage
            await self._track_usage(
                user_id=str(user.id),
                model=model_provider,
                tokens_used=total_tokens,
                task=request.task.value,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Error generating streaming response with {model_provider}: {e}")
            yield self._create_error_response(str(e))
    
    async def _check_rate_limits(self, user: UserResponse, task: LLMTask, db: Session) -> bool:
        """Check rate limits based on user tier"""
        # Get user's current usage
        from datetime import datetime, timedelta
        
        today = datetime.utcnow().date()
        usage = db.query(UsageTracking).filter(
            UsageTracking.user_id == user.id,
            UsageTracking.date == today
        ).first()
        
        if not usage:
            return True  # No usage today, allow request
        
        # Check limits based on subscription tier
        if user.subscription_tier == SubscriptionTier.PRO:
            max_tokens = settings.PRO_TIER_LIMITS["max_llm_tokens_per_month"]
            max_calls = settings.PRO_TIER_LIMITS["max_api_calls_per_day"]
        else:
            max_tokens = settings.FREE_TIER_LIMITS["max_llm_tokens_per_month"]
            max_calls = settings.FREE_TIER_LIMITS["max_api_calls_per_day"]
        
        # Check token limits (approximate)
        if usage.llm_tokens_used >= max_tokens:
            logger.warning(f"Token limit exceeded for user {user.id}")
            return False
        
        # Check API call limits
        if usage.api_calls_count >= max_calls:
            logger.warning(f"API call limit exceeded for user {user.id}")
            return False
        
        return True
    
    async def _track_usage(
        self,
        user_id: str,
        model: str,
        tokens_used: int,
        task: str,
        db: Session
    ):
        """Track LLM usage for billing and limits"""
        try:
            from datetime import datetime
            
            today = datetime.utcnow().date()
            usage = db.query(UsageTracking).filter(
                UsageTracking.user_id == user_id,
                UsageTracking.date == today
            ).first()
            
            if usage:
                usage.llm_tokens_used += tokens_used
                usage.api_calls_count += 1
                usage.updated_at = datetime.utcnow()
            else:
                usage = UsageTracking(
                    user_id=user_id,
                    date=today,
                    llm_tokens_used=tokens_used,
                    api_calls_count=1,
                    storage_used_bytes=0
                )
                db.add(usage)
            
            db.commit()
            logger.debug(f"Tracked usage: {tokens_used} tokens for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
            db.rollback()
    
    def _create_error_response(self, error_message: str) -> LLMResponse:
        """Create error response"""
        return LLMResponse(
            content=f"I apologize, but I encountered an error: {error_message}",
            model_used="error",
            tokens_used=0,
            latency_ms=0,
            confidence_score=0.0,
            metadata={"error": error_message}
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all LLM services"""
        return {
            "ollama": {
                "available": self._model_availability["ollama"],
                "health": await self.ollama_client.health_check() if self._model_availability["ollama"] else False
            },
            "maverick": {
                "available": self._model_availability["maverick"],
                "health": await self.maverick_client.health_check() if self._model_availability["maverick"] else False
            }
        }
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        models = []
        
        if self._model_availability["ollama"]:
            ollama_models = await self.ollama_client.list_models()
            models.extend(ollama_models)
        
        if self._model_availability["maverick"]:
            maverick_models = await self.maverick_client.list_models()
            models.extend(maverick_models)
        
        return models
"""
Ollama Client for Loglytics AI
Handles local Ollama model integration
"""

import httpx
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from app.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for Ollama local LLM integration"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.client = httpx.AsyncClient(timeout=60.0)
        self.available_models = []
        self._model_loaded = False
    
    async def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
                logger.info(f"Ollama health check passed. Available models: {self.available_models}")
                return True
            else:
                logger.warning(f"Ollama health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ollama health check error: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Ollama models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("models", []):
                    models.append({
                        "name": model["name"],
                        "provider": "ollama",
                        "type": "local",
                        "size": model.get("size", "Unknown"),
                        "modified_at": model.get("modified_at"),
                        "available": True
                    })
                return models
            else:
                return []
        except Exception as e:
            logger.error(f"Error listing Ollama models: {e}")
            return []
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        structured_output: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response using Ollama
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            structured_output: Whether to request structured output
            
        Returns:
            Generated response
        """
        try:
            if not model:
                model = settings.DEFAULT_LLM_MODEL
            
            # Ensure model is loaded
            await self._ensure_model_loaded(model)
            
            # Prepare request
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens or 1000,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            # Add structured output format if requested
            if structured_output:
                request_data["format"] = "json"
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "content": data.get("response", ""),
                    "tokens_used": len(data.get("response", "").split()),
                    "model": model,
                    "done": data.get("done", True),
                    "total_duration": data.get("total_duration", 0)
                }
            else:
                logger.error(f"Ollama generation failed: {response.status_code}")
                return {
                    "content": "Error generating response",
                    "tokens_used": 0,
                    "model": model,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return {
                "content": f"Error: {str(e)}",
                "tokens_used": 0,
                "model": model or "unknown",
                "error": str(e)
            }
    
    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming response using Ollama
        
        Args:
            prompt: Input prompt
            model: Model name (uses default if None)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks
        """
        try:
            if not model:
                model = settings.DEFAULT_LLM_MODEL
            
            # Ensure model is loaded
            await self._ensure_model_loaded(model)
            
            # Prepare request
            request_data = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens or 1000,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=request_data
            ) as response:
                if response.status_code == 200:
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk_data = json.loads(line)
                                if "response" in chunk_data:
                                    yield {
                                        "content": chunk_data["response"],
                                        "tokens": 1,  # Approximate
                                        "done": chunk_data.get("done", False)
                                    }
                            except json.JSONDecodeError:
                                continue
                else:
                    yield {
                        "content": f"Error: HTTP {response.status_code}",
                        "tokens": 0,
                        "done": True
                    }
                    
        except Exception as e:
            logger.error(f"Error in Ollama streaming: {e}")
            yield {
                "content": f"Error: {str(e)}",
                "tokens": 0,
                "done": True
            }
    
    async def _ensure_model_loaded(self, model: str):
        """Ensure model is loaded and ready"""
        if not self._model_loaded or model not in self.available_models:
            try:
                # Try to pull the model if not available
                if model not in self.available_models:
                    logger.info(f"Pulling model {model}...")
                    pull_response = await self.client.post(
                        f"{self.base_url}/api/pull",
                        json={"name": model, "stream": False}
                    )
                    if pull_response.status_code == 200:
                        self.available_models.append(model)
                        logger.info(f"Model {model} pulled successfully")
                    else:
                        logger.error(f"Failed to pull model {model}")
                        return
                
                # Load the model
                load_response = await self.client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": "Hello",  # Simple prompt to load model
                        "stream": False
                    }
                )
                
                if load_response.status_code == 200:
                    self._model_loaded = True
                    logger.info(f"Model {model} loaded successfully")
                else:
                    logger.error(f"Failed to load model {model}")
                    
            except Exception as e:
                logger.error(f"Error ensuring model loaded: {e}")
    
    async def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting model info for {model}: {e}")
            return None
    
    async def delete_model(self, model: str) -> bool:
        """Delete a model"""
        try:
            response = await self.client.delete(
                f"{self.base_url}/api/delete",
                json={"name": model}
            )
            
            if response.status_code == 200:
                if model in self.available_models:
                    self.available_models.remove(model)
                logger.info(f"Model {model} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete model {model}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting model {model}: {e}")
            return False
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

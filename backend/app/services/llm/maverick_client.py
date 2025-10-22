"""
Maverick Client for Loglytics AI
Handles Llama 4 Maverick model integration using transformers
"""

import torch
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import gc
import asyncio
from app.config import settings

logger = logging.getLogger(__name__)

class MaverickClient:
    """Client for Llama 4 Maverick model integration"""
    
    def __init__(self):
        self.model_name = "meta-llama/Llama-4-Maverick-8B-Instruct"
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_memory = "16GB"  # 16GB RAM constraint
        self._model_loaded = False
        
        # Configure for 16GB RAM
        self.quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4"
        )
    
    async def health_check(self) -> bool:
        """Check if Maverick model is available and loaded"""
        try:
            if not self._model_loaded:
                await self._load_model()
            return self._model_loaded
        except Exception as e:
            logger.error(f"Maverick health check failed: {e}")
            return False
    
    async def _load_model(self):
        """Load the Maverick model with memory optimization"""
        try:
            logger.info("Loading Llama 4 Maverick model...")
            
            # Check available memory
            if torch.cuda.is_available():
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"GPU memory available: {gpu_memory:.1f}GB")
                
                if gpu_memory < 8:
                    logger.warning("Insufficient GPU memory, using CPU")
                    self.device = "cpu"
            else:
                logger.info("CUDA not available, using CPU")
                self.device = "cpu"
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model with quantization for memory efficiency
            if self.device == "cuda":
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    quantization_config=self.quantization_config,
                    device_map="auto",
                    trust_remote_code=True,
                    torch_dtype=torch.float16
                )
            else:
                # CPU fallback with reduced precision
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float32,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True
                )
                self.model = self.model.to(self.device)
            
            # Create pipeline for easier generation
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
            )
            
            self._model_loaded = True
            logger.info("Maverick model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Maverick model: {e}")
            self._model_loaded = False
            raise
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available Maverick models"""
        return [{
            "name": self.model_name,
            "provider": "maverick",
            "type": "cloud",
            "device": self.device,
            "available": self._model_loaded,
            "quantized": self.device == "cuda"
        }]
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        structured_output: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response using Maverick model
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            structured_output: Whether to request structured output
            
        Returns:
            Generated response
        """
        try:
            if not self._model_loaded:
                await self._load_model()
            
            if not self.pipeline:
                raise ValueError("Model pipeline not initialized")
            
            # Prepare generation parameters
            generation_kwargs = {
                "max_new_tokens": max_tokens or 512,
                "temperature": temperature,
                "top_p": 0.9,
                "top_k": 50,
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "return_full_text": False
            }
            
            # Add structured output format if requested
            if structured_output:
                prompt = f"{prompt}\n\nPlease respond in valid JSON format."
            
            # Generate response
            result = self.pipeline(
                prompt,
                **generation_kwargs
            )
            
            if result and len(result) > 0:
                generated_text = result[0]["generated_text"]
                
                # Count tokens
                input_tokens = len(self.tokenizer.encode(prompt))
                output_tokens = len(self.tokenizer.encode(generated_text))
                total_tokens = input_tokens + output_tokens
                
                return {
                    "content": generated_text.strip(),
                    "tokens_used": output_tokens,
                    "input_tokens": input_tokens,
                    "total_tokens": total_tokens,
                    "model": self.model_name,
                    "device": self.device
                }
            else:
                return {
                    "content": "No response generated",
                    "tokens_used": 0,
                    "model": self.model_name,
                    "error": "Empty response"
                }
                
        except Exception as e:
            logger.error(f"Error generating with Maverick: {e}")
            return {
                "content": f"Error: {str(e)}",
                "tokens_used": 0,
                "model": self.model_name,
                "error": str(e)
            }
    
    async def generate_stream(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate streaming response using Maverick model
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Response chunks
        """
        try:
            if not self._model_loaded:
                await self._load_model()
            
            if not self.pipeline:
                raise ValueError("Model pipeline not initialized")
            
            # For streaming, we'll generate in chunks
            # This is a simplified implementation
            full_response = await self.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Split response into chunks for streaming effect
            content = full_response["content"]
            words = content.split()
            chunk_size = 3  # Words per chunk
            
            for i in range(0, len(words), chunk_size):
                chunk_words = words[i:i + chunk_size]
                chunk_text = " ".join(chunk_words)
                
                if i + chunk_size < len(words):
                    chunk_text += " "
                
                yield {
                    "content": chunk_text,
                    "tokens": len(chunk_text.split()),
                    "done": i + chunk_size >= len(words)
                }
                
                # Small delay to simulate streaming
                await asyncio.sleep(0.05)
                
        except Exception as e:
            logger.error(f"Error in Maverick streaming: {e}")
            yield {
                "content": f"Error: {str(e)}",
                "tokens": 0,
                "done": True
            }
    
    async def batch_generate(
        self,
        prompts: List[str],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate responses for multiple prompts in batch
        
        Args:
            prompts: List of input prompts
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            List of generated responses
        """
        try:
            if not self._model_loaded:
                await self._load_model()
            
            if not self.pipeline:
                raise ValueError("Model pipeline not initialized")
            
            results = []
            
            # Process prompts in smaller batches to manage memory
            batch_size = 4 if self.device == "cuda" else 2
            
            for i in range(0, len(prompts), batch_size):
                batch_prompts = prompts[i:i + batch_size]
                
                # Generate for batch
                batch_results = self.pipeline(
                    batch_prompts,
                    max_new_tokens=max_tokens or 512,
                    temperature=temperature,
                    top_p=0.9,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    return_full_text=False
                )
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, list):
                        result = result[0]
                    
                    generated_text = result.get("generated_text", "")
                    
                    results.append({
                        "content": generated_text.strip(),
                        "tokens_used": len(generated_text.split()),
                        "model": self.model_name,
                        "prompt_index": i + j
                    })
                
                # Clear cache to manage memory
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            return [{"content": f"Error: {str(e)}", "tokens_used": 0} for _ in prompts]
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage"""
        memory_info = {}
        
        if torch.cuda.is_available():
            memory_info["gpu_allocated"] = torch.cuda.memory_allocated() / 1024**3
            memory_info["gpu_reserved"] = torch.cuda.memory_reserved() / 1024**3
            memory_info["gpu_max_allocated"] = torch.cuda.max_memory_allocated() / 1024**3
        
        memory_info["device"] = self.device
        memory_info["model_loaded"] = self._model_loaded
        
        return memory_info
    
    async def unload_model(self):
        """Unload model to free memory"""
        try:
            if self.model:
                del self.model
                self.model = None
            
            if self.tokenizer:
                del self.tokenizer
                self.tokenizer = None
            
            if self.pipeline:
                del self.pipeline
                self.pipeline = None
            
            # Clear CUDA cache
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
            
            self._model_loaded = False
            logger.info("Maverick model unloaded successfully")
            
        except Exception as e:
            logger.error(f"Error unloading Maverick model: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._load_model()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.unload_model()

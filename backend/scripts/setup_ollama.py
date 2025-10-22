#!/usr/bin/env python3
"""
Ollama Local LLM Setup Script for Loglytics AI
This script sets up and verifies the best Ollama model for log analysis on 16GB RAM systems.
"""

import os
import sys
import json
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

# Add the parent directory to the path to import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model recommendations for 16GB RAM
RECOMMENDED_MODELS = [
    {
        "name": "llama3.2:3b",
        "size": "~2.1GB",
        "parameters": "3B",
        "description": "Meta's Llama 3.2 3B - Excellent for log analysis, fast inference",
        "recommended": True
    },
    {
        "name": "phi3:3.8b",
        "size": "~2.3GB", 
        "parameters": "3.8B",
        "description": "Microsoft's Phi-3 3.8B - Great for structured data analysis",
        "recommended": True
    },
    {
        "name": "qwen2.5:3b",
        "size": "~2.0GB",
        "parameters": "3B", 
        "description": "Alibaba's Qwen2.5 3B - Optimized for code and technical tasks",
        "recommended": True
    }
]

# Sample log entries for testing
SAMPLE_LOG_ENTRIES = [
    {
        "level": "ERROR",
        "message": "Database connection failed: Connection timeout after 30 seconds",
        "source": "database",
        "timestamp": "2024-01-15T10:30:45Z"
    },
    {
        "level": "WARN",
        "message": "High memory usage detected: 85% of available memory in use",
        "source": "monitor",
        "timestamp": "2024-01-15T10:31:12Z"
    },
    {
        "level": "INFO",
        "message": "User authentication successful for user_id: 12345",
        "source": "auth",
        "timestamp": "2024-01-15T10:31:45Z"
    },
    {
        "level": "CRITICAL",
        "message": "Application crashed due to null pointer exception in payment module",
        "source": "payment",
        "timestamp": "2024-01-15T10:32:15Z"
    }
]

class OllamaSetup:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.config_dir = Path(__file__).parent.parent / "app" / "config"
        self.config_file = self.config_dir / "llm_config.py"
        
    def check_ollama_running(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Ollama is running and accessible")
                return True
            else:
                logger.error(f"❌ Ollama returned status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Cannot connect to Ollama: {e}")
            logger.info("💡 Please start Ollama by running: ollama serve")
            return False
    
    def get_installed_models(self) -> List[str]:
        """Get list of currently installed models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                logger.info(f"📋 Installed models: {models}")
                return models
            else:
                logger.error(f"❌ Failed to get models: {response.status_code}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error getting models: {e}")
            return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        logger.info(f"🔄 Pulling model: {model_name}")
        logger.info("⏳ This may take several minutes depending on your internet connection...")
        
        try:
            # Use subprocess to get real-time output
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Stream output
            for line in process.stdout:
                if "pulling" in line.lower() or "downloading" in line.lower():
                    logger.info(f"📥 {line.strip()}")
                elif "success" in line.lower() or "complete" in line.lower():
                    logger.info(f"✅ {line.strip()}")
            
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"✅ Successfully pulled model: {model_name}")
                return True
            else:
                logger.error(f"❌ Failed to pull model: {model_name}")
                return False
                
        except FileNotFoundError:
            logger.error("❌ Ollama command not found. Please install Ollama first.")
            logger.info("💡 Install from: https://ollama.ai/download")
            return False
        except Exception as e:
            logger.error(f"❌ Error pulling model: {e}")
            return False
    
    def test_model_inference(self, model_name: str) -> Tuple[bool, Dict]:
        """Test model inference with sample log analysis"""
        logger.info(f"🧪 Testing model inference: {model_name}")
        
        # Create a comprehensive test prompt
        test_prompt = """You are an expert log analyst. Analyze the following log entries and provide insights:

Log Entries:
"""
        
        for i, log in enumerate(SAMPLE_LOG_ENTRIES, 1):
            test_prompt += f"{i}. [{log['level']}] {log['message']} (Source: {log['source']}, Time: {log['timestamp']})\n"
        
        test_prompt += """
Please provide:
1. Summary of issues found
2. Severity assessment
3. Recommended actions
4. Pattern analysis

Keep your response concise but informative."""

        try:
            # Test the model
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get('response', '')
                
                # Calculate performance metrics
                start_time = time.time()
                response_time = time.time() - start_time
                
                # Basic quality checks
                quality_score = self._assess_response_quality(response_text)
                
                result = {
                    "success": True,
                    "response": response_text,
                    "response_time": response_time,
                    "quality_score": quality_score,
                    "tokens_generated": len(response_text.split()),
                    "model_name": model_name
                }
                
                logger.info("✅ Model inference test successful")
                logger.info(f"📊 Response time: {response_time:.2f}s")
                logger.info(f"📊 Quality score: {quality_score}/10")
                logger.info(f"📊 Tokens generated: {result['tokens_generated']}")
                
                return True, result
            else:
                logger.error(f"❌ Model inference failed: {response.status_code}")
                return False, {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error testing model: {e}")
            return False, {}
    
    def _assess_response_quality(self, response: str) -> int:
        """Assess the quality of the model response (1-10 scale)"""
        score = 5  # Base score
        
        # Check for key elements
        if "summary" in response.lower() or "issues" in response.lower():
            score += 1
        if "severity" in response.lower() or "critical" in response.lower():
            score += 1
        if "recommend" in response.lower() or "action" in response.lower():
            score += 1
        if "pattern" in response.lower() or "analysis" in response.lower():
            score += 1
        if len(response) > 100:  # Substantial response
            score += 1
        if "error" in response.lower() or "warn" in response.lower():
            score += 1
        
        return min(score, 10)
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get detailed information about a model"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/show",
                json={"name": model_name},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Could not get model info: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error getting model info: {e}")
            return None
    
    def create_llm_config(self, model_name: str, test_results: Dict) -> bool:
        """Create LLM configuration file"""
        try:
            # Ensure config directory exists
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            # Get model info
            model_info = self.get_model_info(model_name)
            
            config_content = f'''"""
LLM Configuration for Loglytics AI
Generated by setup_ollama.py
"""

from typing import Dict, Any
from app.config import settings

# Ollama Configuration
OLLAMA_CONFIG = {{
    "base_url": "http://localhost:11434",
    "model_name": "{model_name}",
    "timeout": 60,
    "max_retries": 3,
    "temperature": 0.3,
    "top_p": 0.9,
    "max_tokens": 2000,
    "stream": False
}}

# Model Information
MODEL_INFO = {{
    "name": "{model_name}",
    "type": "ollama",
    "provider": "local",
    "size": "{model_info.get('size', 'Unknown') if model_info else 'Unknown'}",
    "parameters": "{model_info.get('parameter_size', 'Unknown') if model_info else 'Unknown'}",
    "family": "{model_name.split(':')[0]}",
    "version": "{model_name.split(':')[1] if ':' in model_name else 'latest'}",
    "recommended_for": "log_analysis",
    "performance": {{
        "response_time": {test_results.get('response_time', 0):.2f},
        "quality_score": {test_results.get('quality_score', 0)},
        "tokens_generated": {test_results.get('tokens_generated', 0)}
    }}
}}

# Log Analysis Specific Prompts
LOG_ANALYSIS_PROMPTS = {{
    "system_prompt": """You are Loglytics AI, an expert log analysis assistant. You help users understand their logs, identify issues, and provide actionable insights.

Your capabilities:
- Analyze log patterns and anomalies
- Identify errors, warnings, and critical issues
- Provide root cause analysis
- Suggest remediation steps
- Detect security threats
- Monitor system health

Always provide clear, actionable insights based on the log data provided.""",
    
    "analysis_prompt": """Analyze the following log entries and provide insights:

{{log_entries}}

Please provide:
1. **Summary**: Brief overview of the log data
2. **Issues Found**: List of errors, warnings, and critical issues
3. **Severity Assessment**: Rate the severity of each issue
4. **Root Cause Analysis**: Likely causes of the issues
5. **Recommendations**: Specific actions to resolve issues
6. **Pattern Analysis**: Any recurring patterns or trends
7. **Security Concerns**: Potential security issues

Format your response clearly with headers and bullet points.""",
    
    "chat_prompt": """Based on the log data and context, answer the user's question about their logs.

Context: {{context}}
Question: {{question}}

Provide a helpful, accurate response based on the log analysis.""",
    
    "anomaly_detection": """Detect anomalies in the following log entries:

{{log_entries}}

Look for:
- Unusual patterns or frequencies
- Error spikes
- Performance degradation indicators
- Security anomalies
- System health issues

Provide a detailed analysis of any anomalies found."""
}}

# Performance Settings
PERFORMANCE_SETTINGS = {{
    "batch_size": 10,
    "concurrent_requests": 3,
    "cache_responses": True,
    "cache_ttl": 3600,  # 1 hour
    "enable_streaming": False,
    "enable_parallel_processing": True
}}

# Error Handling
ERROR_HANDLINGS = {{
    "max_retries": 3,
    "retry_delay": 1.0,
    "fallback_model": None,
    "timeout_handling": "retry",
    "rate_limit_handling": "exponential_backoff"
}}

def get_ollama_config() -> Dict[str, Any]:
    """Get Ollama configuration"""
    return OLLAMA_CONFIG

def get_model_info() -> Dict[str, Any]:
    """Get model information"""
    return MODEL_INFO

def get_log_analysis_prompts() -> Dict[str, str]:
    """Get log analysis prompts"""
    return LOG_ANALYSIS_PROMPTS

def get_performance_settings() -> Dict[str, Any]:
    """Get performance settings"""
    return PERFORMANCE_SETTINGS

def get_error_handling() -> Dict[str, Any]:
    """Get error handling settings"""
    return ERROR_HANDLINGS
'''
            
            # Write config file
            with open(self.config_file, 'w') as f:
                f.write(config_content)
            
            logger.info(f"✅ LLM configuration saved to: {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating config file: {e}")
            return False
    
    def print_model_recommendations(self):
        """Print model recommendations"""
        logger.info("🤖 Recommended Models for 16GB RAM:")
        logger.info("=" * 60)
        
        for i, model in enumerate(RECOMMENDED_MODELS, 1):
            status = "⭐ RECOMMENDED" if model["recommended"] else ""
            logger.info(f"{i}. {model['name']} {status}")
            logger.info(f"   Size: {model['size']}")
            logger.info(f"   Parameters: {model['parameters']}")
            logger.info(f"   Description: {model['description']}")
            logger.info("")
    
    def run_setup(self) -> bool:
        """Run the complete setup process"""
        logger.info("🚀 Starting Ollama LLM Setup for Loglytics AI")
        logger.info("=" * 60)
        
        # Print recommendations
        self.print_model_recommendations()
        
        # Check if Ollama is running
        if not self.check_ollama_running():
            return False
        
        # Get installed models
        installed_models = self.get_installed_models()
        
        # Find the best available model
        selected_model = None
        for model in RECOMMENDED_MODELS:
            if model["name"] in installed_models:
                selected_model = model["name"]
                logger.info(f"✅ Found installed model: {selected_model}")
                break
        
        # If no recommended model is installed, pull the first one
        if not selected_model:
            logger.info("📥 No recommended models found. Pulling the first recommended model...")
            selected_model = RECOMMENDED_MODELS[0]["name"]
            
            if not self.pull_model(selected_model):
                return False
        
        # Test the model
        logger.info(f"🧪 Testing model: {selected_model}")
        success, test_results = self.test_model_inference(selected_model)
        
        if not success:
            logger.error("❌ Model test failed")
            return False
        
        # Print test results
        logger.info("📊 Test Results:")
        logger.info(f"   Model: {selected_model}")
        logger.info(f"   Response Time: {test_results['response_time']:.2f}s")
        logger.info(f"   Quality Score: {test_results['quality_score']}/10")
        logger.info(f"   Tokens Generated: {test_results['tokens_generated']}")
        
        # Show sample response
        logger.info("📝 Sample Response:")
        logger.info("-" * 40)
        logger.info(test_results['response'][:500] + "..." if len(test_results['response']) > 500 else test_results['response'])
        logger.info("-" * 40)
        
        # Create configuration file
        if not self.create_llm_config(selected_model, test_results):
            return False
        
        # Final success message
        logger.info("🎉 Ollama LLM setup completed successfully!")
        logger.info("=" * 60)
        logger.info(f"✅ Model: {selected_model}")
        logger.info(f"✅ Configuration: {self.config_file}")
        logger.info("✅ Ready for log analysis!")
        logger.info("")
        logger.info("💡 Next steps:")
        logger.info("   1. Start your FastAPI application")
        logger.info("   2. Test the LLM integration")
        logger.info("   3. Upload some log files for analysis")
        
        return True

def main():
    """Main function"""
    setup = OllamaSetup()
    
    try:
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏹️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

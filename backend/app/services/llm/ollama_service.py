"""
Ollama LLM Service for Loglytics AI
Provides local LLM capabilities using Ollama
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any, AsyncGenerator
from sqlalchemy.orm import Session
import logging

from app.config.llm_config import (
    get_ollama_config, 
    get_log_analysis_prompts, 
    get_performance_settings,
    get_error_handling
)

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self, db: Session):
        self.db = db
        self.config = get_ollama_config()
        self.prompts = get_log_analysis_prompts()
        self.performance = get_performance_settings()
        self.error_handling = get_error_handling()
        self.base_url = self.config["base_url"]
        self.model_name = self.config["model_name"]
        
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate a response using Ollama"""
        try:
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt, system_prompt)
            
            # Prepare request data
            request_data = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature or self.config["temperature"],
                    "top_p": self.config["top_p"],
                    "num_predict": max_tokens or self.config["max_tokens"]
                }
            }
            
            # Make request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=self.config["timeout"]
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data.get("response", ""),
                    "model": self.model_name,
                    "tokens_generated": len(data.get("response", "").split()),
                    "response_time": data.get("total_duration", 0) / 1e9,  # Convert nanoseconds to seconds
                    "metadata": {
                        "prompt_tokens": len(full_prompt.split()),
                        "temperature": request_data["options"]["temperature"],
                        "stream": stream
                    }
                }
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "content": ""
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request error: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
        except Exception as e:
            logger.error(f"Unexpected error in Ollama service: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
    
    async def analyze_logs(
        self, 
        log_entries: List[Dict[str, Any]], 
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """Analyze log entries using Ollama"""
        try:
            # Format log entries
            formatted_logs = self._format_log_entries(log_entries)
            
            # Get appropriate prompt
            if analysis_type == "anomaly":
                prompt_template = self.prompts["anomaly_detection"]
            else:
                prompt_template = self.prompts["analysis_prompt"]
            
            prompt = prompt_template.format(log_entries=formatted_logs)
            
            # Generate analysis
            result = await self.generate_response(
                prompt=prompt,
                system_prompt=self.prompts["system_prompt"],
                temperature=0.3  # Lower temperature for analysis
            )
            
            if result["success"]:
                # Parse the response for structured data
                parsed_analysis = self._parse_analysis_response(result["content"])
                result.update(parsed_analysis)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing logs: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
    
    async def chat_response(
        self, 
        message: str, 
        context: Optional[str] = None,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate a chat response using Ollama"""
        try:
            # Prepare context
            context_str = context or "No specific context provided."
            
            # Prepare chat history
            history_str = ""
            if chat_history:
                for msg in chat_history[-5:]:  # Last 5 messages
                    role = msg.get("role", "user")
                    content = msg.get("content", "")
                    history_str += f"{role}: {content}\n"
            
            # Create prompt
            prompt = self.prompts["chat_prompt"].format(
                context=context_str,
                question=message
            )
            
            if history_str:
                prompt = f"Previous conversation:\n{history_str}\n\n{prompt}"
            
            # Generate response
            result = await self.generate_response(
                prompt=prompt,
                system_prompt=self.prompts["system_prompt"],
                temperature=0.7  # Higher temperature for chat
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
    
    async def detect_anomalies(
        self, 
        log_entries: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect anomalies in log entries"""
        return await self.analyze_logs(log_entries, analysis_type="anomaly")
    
    async def generate_insights(
        self, 
        log_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate insights from log data"""
        try:
            # Format the data
            data_str = json.dumps(log_data, indent=2)
            
            prompt = f"""Based on the following log analysis data, provide actionable insights:

{data_str}

Focus on:
1. Key findings and patterns
2. Potential issues and risks
3. Optimization opportunities
4. Recommended actions
5. Security concerns

Provide clear, actionable recommendations."""

            result = await self.generate_response(
                prompt=prompt,
                system_prompt=self.prompts["system_prompt"],
                temperature=0.5
            )
            
            if result["success"]:
                # Parse insights
                insights = self._parse_insights_response(result["content"])
                result.update(insights)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": ""
            }
    
    def _prepare_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Prepare the full prompt with system message"""
        if system_prompt:
            return f"System: {system_prompt}\n\nUser: {prompt}"
        return prompt
    
    def _format_log_entries(self, log_entries: List[Dict[str, Any]]) -> str:
        """Format log entries for analysis"""
        formatted = []
        for i, entry in enumerate(log_entries, 1):
            level = entry.get("level", "UNKNOWN")
            message = entry.get("message", "")
            source = entry.get("source", "unknown")
            timestamp = entry.get("timestamp", "")
            
            formatted.append(f"{i}. [{level}] {message} (Source: {source}, Time: {timestamp})")
        
        return "\n".join(formatted)
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse analysis response for structured data"""
        try:
            # Extract key sections
            sections = {
                "summary": self._extract_section(response, ["summary", "overview"]),
                "issues": self._extract_section(response, ["issues", "problems", "errors"]),
                "severity": self._extract_section(response, ["severity", "criticality"]),
                "recommendations": self._extract_section(response, ["recommendations", "actions", "solutions"]),
                "patterns": self._extract_section(response, ["patterns", "trends", "analysis"])
            }
            
            # Count issues by severity
            severity_counts = self._count_severity_issues(response)
            
            return {
                "sections": sections,
                "severity_counts": severity_counts,
                "structured": True
            }
            
        except Exception as e:
            logger.warning(f"Error parsing analysis response: {e}")
            return {"structured": False}
    
    def _parse_insights_response(self, response: str) -> Dict[str, Any]:
        """Parse insights response for structured data"""
        try:
            insights = {
                "key_findings": self._extract_section(response, ["findings", "key findings"]),
                "risks": self._extract_section(response, ["risks", "threats"]),
                "opportunities": self._extract_section(response, ["opportunities", "optimizations"]),
                "recommendations": self._extract_section(response, ["recommendations", "actions"]),
                "security": self._extract_section(response, ["security", "vulnerabilities"])
            }
            
            return {
                "insights": insights,
                "structured": True
            }
            
        except Exception as e:
            logger.warning(f"Error parsing insights response: {e}")
            return {"structured": False}
    
    def _extract_section(self, text: str, keywords: List[str]) -> str:
        """Extract a section from response based on keywords"""
        lines = text.split('\n')
        section_lines = []
        in_section = False
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                in_section = True
                section_lines.append(line)
            elif in_section and line.strip() and not line.startswith(' '):
                # Check if we've moved to a new section
                if any(keyword in line_lower for keyword in ['summary', 'issues', 'recommendations', 'patterns', 'security']):
                    break
                section_lines.append(line)
            elif in_section and line.strip():
                section_lines.append(line)
        
        return '\n'.join(section_lines).strip()
    
    def _count_severity_issues(self, response: str) -> Dict[str, int]:
        """Count issues by severity level"""
        severity_counts = {
            "critical": 0,
            "error": 0,
            "warning": 0,
            "info": 0
        }
        
        response_lower = response.lower()
        for severity in severity_counts:
            severity_counts[severity] = response_lower.count(severity)
        
        return severity_counts
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Ollama service is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                
                return {
                    "healthy": True,
                    "model_available": self.model_name in models,
                    "available_models": models,
                    "current_model": self.model_name
                }
            else:
                return {
                    "healthy": False,
                    "error": f"API returned {response.status_code}",
                    "model_available": False
                }
                
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e),
                "model_available": False
            }

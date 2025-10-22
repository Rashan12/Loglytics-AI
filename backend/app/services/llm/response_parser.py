"""
Response Parser for Loglytics AI
Parses and structures LLM responses
"""

import json
import re
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParsedResponse:
    """Parsed LLM response structure"""
    content: str
    structured_data: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.8
    tokens_used: int = 0
    metadata: Dict[str, Any] = None

class ResponseParser:
    """Parses and structures LLM responses"""
    
    def __init__(self):
        self.json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```',     # JSON in generic code blocks
            r'(\{[^{}]*"[^"]*"[^{}]*\})',  # Simple JSON objects
            r'(\[.*?\])',                  # JSON arrays
        ]
    
    def parse_response(
        self,
        response: Dict[str, Any],
        task: str,
        structured_output: bool = False
    ) -> Dict[str, Any]:
        """
        Parse LLM response based on task and output format
        
        Args:
            response: Raw LLM response
            task: Task type
            structured_output: Whether response should be structured
            
        Returns:
            Parsed response dictionary
        """
        try:
            content = response.get("content", "")
            tokens_used = response.get("tokens_used", 0)
            
            # Extract structured data if requested
            structured_data = None
            if structured_output:
                structured_data = self._extract_structured_data(content)
            
            # Parse content based on task
            parsed_content = self._parse_content_by_task(content, task)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                content, task, structured_data
            )
            
            return {
                "content": parsed_content,
                "structured_data": structured_data,
                "confidence_score": confidence_score,
                "tokens_used": tokens_used,
                "metadata": {
                    "task": task,
                    "structured_output": structured_output,
                    "parsing_success": structured_data is not None if structured_output else True
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                "content": response.get("content", ""),
                "structured_data": None,
                "confidence_score": 0.5,
                "tokens_used": response.get("tokens_used", 0),
                "metadata": {"error": str(e)}
            }
    
    def _extract_structured_data(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract structured data from response content"""
        try:
            # Try to find JSON in the content
            for pattern in self.json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match)
                        if isinstance(data, (dict, list)):
                            return data
                    except json.JSONDecodeError:
                        continue
            
            # Try to parse the entire content as JSON
            try:
                data = json.loads(content)
                if isinstance(data, (dict, list)):
                    return data
            except json.JSONDecodeError:
                pass
            
            # Try to extract JSON from the end of the content
            lines = content.split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{') or line.startswith('['):
                    try:
                        data = json.loads(line)
                        if isinstance(data, (dict, list)):
                            return data
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return None
    
    def _parse_content_by_task(self, content: str, task: str) -> str:
        """Parse content based on specific task requirements"""
        try:
            if task == "log_analysis":
                return self._parse_log_analysis_content(content)
            elif task == "error_detection":
                return self._parse_error_detection_content(content)
            elif task == "root_cause":
                return self._parse_root_cause_content(content)
            elif task == "anomaly_detection":
                return self._parse_anomaly_detection_content(content)
            elif task == "natural_query":
                return self._parse_natural_query_content(content)
            elif task == "summarization":
                return self._parse_summarization_content(content)
            elif task == "chat":
                return self._parse_chat_content(content)
            else:
                return content
                
        except Exception as e:
            logger.error(f"Error parsing content for task {task}: {e}")
            return content
    
    def _parse_log_analysis_content(self, content: str) -> str:
        """Parse log analysis content"""
        # Extract key sections
        sections = self._extract_sections(content, [
            "summary", "analysis", "issues", "problems",
            "recommendations", "suggestions", "patterns"
        ])
        
        if sections:
            return self._format_sections(sections)
        
        return content
    
    def _parse_error_detection_content(self, content: str) -> str:
        """Parse error detection content"""
        # Look for error counts and categories
        error_info = self._extract_error_info(content)
        
        if error_info:
            formatted = "Error Detection Results:\n"
            for error_type, count in error_info.items():
                formatted += f"- {error_type}: {count} occurrences\n"
            return formatted
        
        return content
    
    def _parse_root_cause_content(self, content: str) -> str:
        """Parse root cause analysis content"""
        # Extract root cause and evidence
        root_cause = self._extract_root_cause(content)
        
        if root_cause:
            return f"Root Cause: {root_cause['cause']}\n\nEvidence: {root_cause['evidence']}"
        
        return content
    
    def _parse_anomaly_detection_content(self, content: str) -> str:
        """Parse anomaly detection content"""
        # Extract anomalies and their descriptions
        anomalies = self._extract_anomalies(content)
        
        if anomalies:
            formatted = "Detected Anomalies:\n"
            for i, anomaly in enumerate(anomalies, 1):
                formatted += f"{i}. {anomaly}\n"
            return formatted
        
        return content
    
    def _parse_natural_query_content(self, content: str) -> str:
        """Parse natural query content"""
        # Extract direct answers
        answers = self._extract_answers(content)
        
        if answers:
            return "\n".join(answers)
        
        return content
    
    def _parse_summarization_content(self, content: str) -> str:
        """Parse summarization content"""
        # Extract key metrics and highlights
        metrics = self._extract_metrics(content)
        highlights = self._extract_highlights(content)
        
        formatted = "Summary:\n"
        if metrics:
            formatted += f"Key Metrics: {metrics}\n"
        if highlights:
            formatted += f"Highlights: {highlights}\n"
        
        return formatted if metrics or highlights else content
    
    def _parse_chat_content(self, content: str) -> str:
        """Parse chat content"""
        # Clean up chat response
        return content.strip()
    
    def _extract_sections(self, content: str, keywords: List[str]) -> Dict[str, str]:
        """Extract sections from content based on keywords"""
        sections = {}
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if this line starts a new section
            for keyword in keywords:
                if keyword in line_lower and (line.startswith('#') or line.startswith('*') or line.startswith('-')):
                    # Save previous section
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = keyword
                    current_content = [line]
                    break
            else:
                # Add to current section
                if current_section:
                    current_content.append(line)
                elif current_content:
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _format_sections(self, sections: Dict[str, str]) -> str:
        """Format extracted sections"""
        formatted = ""
        for section, content in sections.items():
            formatted += f"## {section.title()}\n{content}\n\n"
        return formatted.strip()
    
    def _extract_error_info(self, content: str) -> Dict[str, int]:
        """Extract error information from content"""
        error_info = {}
        
        # Look for error patterns
        error_patterns = [
            r'(\d+)\s+(?:errors?|failures?)',
            r'(?:error|failure)s?\s*:\s*(\d+)',
            r'(\d+)\s+(?:critical|high|medium|low)\s+(?:errors?|issues?)'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    count = int(match)
                    error_info[f"Total errors"] = error_info.get("Total errors", 0) + count
                except ValueError:
                    continue
        
        return error_info
    
    def _extract_root_cause(self, content: str) -> Optional[Dict[str, str]]:
        """Extract root cause information"""
        # Look for root cause patterns
        patterns = [
            r'root cause[:\s]+(.+?)(?:\n|$)',
            r'underlying cause[:\s]+(.+?)(?:\n|$)',
            r'primary cause[:\s]+(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                cause = match.group(1).strip()
                # Look for evidence
                evidence_pattern = r'evidence[:\s]+(.+?)(?:\n|$)'
                evidence_match = re.search(evidence_pattern, content, re.IGNORECASE | re.DOTALL)
                evidence = evidence_match.group(1).strip() if evidence_match else "Not specified"
                
                return {"cause": cause, "evidence": evidence}
        
        return None
    
    def _extract_anomalies(self, content: str) -> List[str]:
        """Extract anomalies from content"""
        anomalies = []
        
        # Look for anomaly patterns
        patterns = [
            r'anomaly[:\s]+(.+?)(?:\n|$)',
            r'unusual[:\s]+(.+?)(?:\n|$)',
            r'outlier[:\s]+(.+?)(?:\n|$)',
            r'deviation[:\s]+(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                anomaly = match.strip()
                if anomaly and len(anomaly) > 10:  # Filter out very short matches
                    anomalies.append(anomaly)
        
        return anomalies
    
    def _extract_answers(self, content: str) -> List[str]:
        """Extract direct answers from content"""
        answers = []
        
        # Look for answer patterns
        patterns = [
            r'answer[:\s]+(.+?)(?:\n|$)',
            r'result[:\s]+(.+?)(?:\n|$)',
            r'found[:\s]+(.+?)(?:\n|$)',
            r'detected[:\s]+(.+?)(?:\n|$)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                answer = match.strip()
                if answer and len(answer) > 5:
                    answers.append(answer)
        
        return answers
    
    def _extract_metrics(self, content: str) -> Optional[str]:
        """Extract metrics from content"""
        # Look for metric patterns
        patterns = [
            r'(\d+(?:\.\d+)?%)\s+(?:error rate|success rate|uptime)',
            r'(\d+)\s+(?:requests?|errors?|warnings?)',
            r'(\d+(?:\.\d+)?)\s*(?:ms|seconds?|minutes?|hours?)'
        ]
        
        metrics = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            metrics.extend(matches)
        
        return ", ".join(metrics) if metrics else None
    
    def _extract_highlights(self, content: str) -> Optional[str]:
        """Extract highlights from content"""
        # Look for highlight patterns
        patterns = [
            r'highlight[:\s]+(.+?)(?:\n|$)',
            r'key point[:\s]+(.+?)(?:\n|$)',
            r'important[:\s]+(.+?)(?:\n|$)'
        ]
        
        highlights = []
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                highlight = match.strip()
                if highlight and len(highlight) > 10:
                    highlights.append(highlight)
        
        return "; ".join(highlights) if highlights else None
    
    def _calculate_confidence_score(
        self,
        content: str,
        task: str,
        structured_data: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the response"""
        score = 0.5  # Base score
        
        # Length check
        if len(content) > 50:
            score += 0.1
        
        # Structured data check
        if structured_data:
            score += 0.2
        
        # Task-specific checks
        if task == "log_analysis":
            if any(keyword in content.lower() for keyword in ["error", "warning", "issue", "problem"]):
                score += 0.1
            if any(keyword in content.lower() for keyword in ["recommend", "suggest", "fix", "solution"]):
                score += 0.1
        
        elif task == "error_detection":
            if re.search(r'\d+\s+(?:errors?|failures?)', content, re.IGNORECASE):
                score += 0.2
        
        elif task == "root_cause":
            if any(keyword in content.lower() for keyword in ["root cause", "underlying", "primary"]):
                score += 0.2
        
        elif task == "anomaly_detection":
            if any(keyword in content.lower() for keyword in ["anomaly", "unusual", "outlier"]):
                score += 0.2
        
        # JSON structure check
        if structured_data and isinstance(structured_data, dict):
            if "summary" in structured_data or "analysis" in structured_data:
                score += 0.1
        
        return min(score, 1.0)
    
    def validate_structured_output(
        self,
        data: Dict[str, Any],
        task: str
    ) -> bool:
        """Validate structured output against task requirements"""
        try:
            if task == "log_analysis":
                required_fields = ["summary", "issues"]
                return all(field in data for field in required_fields)
            
            elif task == "error_detection":
                required_fields = ["errors"]
                return all(field in data for field in required_fields)
            
            elif task == "root_cause":
                required_fields = ["root_cause"]
                return all(field in data for field in required_fields)
            
            elif task == "anomaly_detection":
                required_fields = ["anomalies"]
                return all(field in data for field in required_fields)
            
            elif task == "natural_query":
                required_fields = ["query", "results"]
                return all(field in data for field in required_fields)
            
            elif task == "summarization":
                required_fields = ["summary"]
                return all(field in data for field in required_fields)
            
            elif task == "chat":
                required_fields = ["response"]
                return all(field in data for field in required_fields)
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating structured output: {e}")
            return False

"""
JSON Log Parser for Loglytics AI
Parses JSON formatted log entries
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class JSONLogParser:
    """Parser for JSON formatted log entries"""
    
    def __init__(self):
        self.required_fields = ["timestamp", "level", "message"]
        self.optional_fields = ["service", "source", "logger", "thread", "correlation_id", "request_id", "user_id"]
        self.timestamp_fields = ["timestamp", "time", "@timestamp", "datetime", "date", "ts"]
        self.level_fields = ["level", "severity", "log_level", "priority"]
        self.message_fields = ["message", "msg", "text", "content", "body", "description"]
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse JSON log content
        
        Args:
            content: JSON log content
            
        Returns:
            List of parsed log entries
        """
        try:
            lines = content.strip().split('\n')
            parsed_entries = []
            
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = self._parse_json_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing JSON line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"JSON parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            logger.info(f"Parsed {len(parsed_entries)} JSON log entries")
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing JSON content: {e}")
            return []
    
    def _parse_json_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single JSON log line"""
        try:
            # Parse JSON
            data = json.loads(line.strip())
            
            if not isinstance(data, dict):
                raise ValueError("JSON log entry must be an object")
            
            # Extract timestamp
            timestamp = self._extract_timestamp(data)
            
            # Extract log level
            log_level = self._extract_log_level(data)
            
            # Extract message
            message = self._extract_message(data)
            
            # Extract source
            source = self._extract_source(data)
            
            # Extract service
            service = self._extract_service(data)
            
            # Extract metadata
            metadata = self._extract_metadata(data)
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": timestamp,
                "level": log_level,
                "message": message,
                "source": source,
                "service": service,
                "metadata": metadata
            }
            
        except json.JSONDecodeError as e:
            logger.debug(f"JSON decode error on line {line_num}: {e}")
            return None
        except Exception as e:
            logger.debug(f"Error parsing JSON line {line_num}: {e}")
            return None
    
    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract timestamp from JSON data"""
        try:
            for field in self.timestamp_fields:
                if field in data and data[field]:
                    timestamp = data[field]
                    return self._parse_timestamp(timestamp)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting timestamp: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: Union[str, datetime, int, float]) -> Optional[str]:
        """Parse timestamp to ISO format"""
        try:
            if isinstance(timestamp, datetime):
                return timestamp.isoformat() + "Z"
            
            if isinstance(timestamp, (int, float)):
                # Unix timestamp
                dt = datetime.fromtimestamp(timestamp)
                return dt.isoformat() + "Z"
            
            if isinstance(timestamp, str):
                # Try dateutil parser
                try:
                    parsed = date_parser.parse(timestamp)
                    return parsed.isoformat() + "Z"
                except (ValueError, TypeError):
                    pass
                
                # Try common formats
                formats = [
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%S.%f%z",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M:%S.%f",
                    "%Y-%m-%d %H:%M:%S.%f%z",
                    "%Y-%m-%d %H:%M:%S%z"
                ]
                
                for fmt in formats:
                    try:
                        parsed = datetime.strptime(timestamp, fmt)
                        return parsed.isoformat() + "Z"
                    except ValueError:
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing timestamp: {e}")
            return None
    
    def _extract_log_level(self, data: Dict[str, Any]) -> str:
        """Extract log level from JSON data"""
        try:
            for field in self.level_fields:
                if field in data and data[field]:
                    level = str(data[field]).strip().upper()
                    return self._normalize_log_level(level)
            
            # Try to extract from message
            if "message" in data:
                level = self._extract_level_from_message(data["message"])
                if level:
                    return level
            
            return "INFO"
            
        except Exception as e:
            logger.debug(f"Error extracting log level: {e}")
            return "INFO"
    
    def _normalize_log_level(self, level: str) -> str:
        """Normalize log level to standard format"""
        level_mapping = {
            "TRACE": "TRACE",
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "WARN": "WARN",
            "WARNING": "WARN",
            "ERROR": "ERROR",
            "CRITICAL": "CRITICAL",
            "FATAL": "FATAL",
            "EMERGENCY": "EMERGENCY",
            "ALERT": "ALERT",
            "NOTICE": "NOTICE",
            "0": "EMERGENCY",
            "1": "ALERT",
            "2": "CRITICAL",
            "3": "ERROR",
            "4": "WARNING",
            "5": "NOTICE",
            "6": "INFO",
            "7": "DEBUG"
        }
        
        return level_mapping.get(level.upper(), "INFO")
    
    def _extract_level_from_message(self, message: str) -> Optional[str]:
        """Extract log level from message content"""
        try:
            message_lower = message.lower()
            
            if any(keyword in message_lower for keyword in ["error", "exception", "failed", "failure"]):
                return "ERROR"
            elif any(keyword in message_lower for keyword in ["warning", "warn", "caution"]):
                return "WARN"
            elif any(keyword in message_lower for keyword in ["info", "information"]):
                return "INFO"
            elif any(keyword in message_lower for keyword in ["debug", "trace"]):
                return "DEBUG"
            elif any(keyword in message_lower for keyword in ["critical", "fatal"]):
                return "CRITICAL"
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting level from message: {e}")
            return None
    
    def _extract_message(self, data: Dict[str, Any]) -> str:
        """Extract message from JSON data"""
        try:
            for field in self.message_fields:
                if field in data and data[field]:
                    message = str(data[field]).strip()
                    if message:
                        return message
            
            # If no message field found, use the entire data as message
            return json.dumps(data, default=str)
            
        except Exception as e:
            logger.debug(f"Error extracting message: {e}")
            return str(data)
    
    def _extract_source(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract source from JSON data"""
        try:
            source_fields = ["source", "logger", "component", "module", "class", "file", "function"]
            
            for field in source_fields:
                if field in data and data[field]:
                    source = str(data[field]).strip()
                    if source:
                        return source
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting source: {e}")
            return None
    
    def _extract_service(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract service from JSON data"""
        try:
            service_fields = ["service", "app", "application", "microservice", "container", "pod", "namespace"]
            
            for field in service_fields:
                if field in data and data[field]:
                    service = str(data[field]).strip()
                    if service:
                        return service
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting service: {e}")
            return None
    
    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from JSON data"""
        try:
            metadata = {}
            
            # Copy all fields that aren't part of the standard schema
            standard_fields = ["timestamp", "time", "@timestamp", "datetime", "date", "ts",
                             "level", "severity", "log_level", "priority",
                             "message", "msg", "text", "content", "body", "description",
                             "source", "logger", "component", "module", "class", "file", "function",
                             "service", "app", "application", "microservice", "container", "pod", "namespace"]
            
            for key, value in data.items():
                if key not in standard_fields:
                    metadata[key] = value
            
            # Add JSON-specific fields
            if "logger" in data:
                metadata["logger"] = data["logger"]
            if "thread" in data:
                metadata["thread"] = data["thread"]
            if "correlation_id" in data:
                metadata["correlation_id"] = data["correlation_id"]
            if "request_id" in data:
                metadata["request_id"] = data["request_id"]
            if "user_id" in data:
                metadata["user_id"] = data["user_id"]
            
            return metadata
            
        except Exception as e:
            logger.debug(f"Error extracting metadata: {e}")
            return {}
    
    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """Validate JSON log schema"""
        try:
            # Check if it's a dictionary
            if not isinstance(data, dict):
                return False
            
            # Check for at least one timestamp field
            has_timestamp = any(field in data for field in self.timestamp_fields)
            
            # Check for at least one message field
            has_message = any(field in data for field in self.message_fields)
            
            return has_timestamp and has_message
            
        except Exception as e:
            logger.debug(f"Error validating schema: {e}")
            return False
    
    def get_schema_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about the JSON schema"""
        try:
            schema_info = {
                "fields": list(data.keys()),
                "field_count": len(data),
                "has_timestamp": any(field in data for field in self.timestamp_fields),
                "has_level": any(field in data for field in self.level_fields),
                "has_message": any(field in data for field in self.message_fields),
                "has_source": any(field in data for field in ["source", "logger", "component", "module", "class", "file", "function"]),
                "has_service": any(field in data for field in ["service", "app", "application", "microservice", "container", "pod", "namespace"])
            }
            
            return schema_info
            
        except Exception as e:
            logger.debug(f"Error getting schema info: {e}")
            return {}
    
    def parse_batch(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse a batch of JSON lines"""
        try:
            parsed_entries = []
            
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = self._parse_json_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing JSON line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"JSON parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing JSON batch: {e}")
            return []

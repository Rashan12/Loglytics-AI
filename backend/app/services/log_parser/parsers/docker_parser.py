"""
Docker Log Parser for Loglytics AI
Parses Docker container logs
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class DockerLogParser:
    """Parser for Docker container log entries"""
    
    def __init__(self):
        # Docker log format with timestamp
        self.docker_timestamp_pattern = re.compile(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'
        )
        
        # Docker log format without timestamp
        self.docker_simple_pattern = re.compile(
            r'^(\S+)\s+(.+)$'
        )
        
        # Container indicators
        self.container_indicators = ["container", "docker", "pod", "k8s", "kubernetes"]
        
        # Log level mapping
        self.log_levels = {
            "trace": "TRACE",
            "debug": "DEBUG",
            "info": "INFO",
            "information": "INFO",
            "warn": "WARNING",
            "warning": "WARNING",
            "error": "ERROR",
            "critical": "CRITICAL",
            "fatal": "FATAL",
            "emergency": "EMERGENCY",
            "alert": "ALERT",
            "notice": "NOTICE",
            "verbose": "DEBUG",
            "severe": "CRITICAL"
        }
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse Docker log content
        
        Args:
            content: Docker log content
            
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
                    entry = self._parse_docker_log_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing Docker log line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Docker log parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            logger.info(f"Parsed {len(parsed_entries)} Docker log entries")
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing Docker log content: {e}")
            return []
    
    def _parse_docker_log_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single Docker log line"""
        try:
            # Try Docker format with timestamp
            match = self.docker_timestamp_pattern.match(line.strip())
            if match:
                return self._parse_docker_with_timestamp(match, line, line_num)
            
            # Try Docker format without timestamp
            match = self.docker_simple_pattern.match(line.strip())
            if match:
                return self._parse_docker_simple(match, line, line_num)
            
            # Try to parse as generic Docker log
            return self._parse_generic_docker_log(line, line_num)
            
        except Exception as e:
            logger.debug(f"Error parsing Docker log line {line_num}: {e}")
            return None
    
    def _parse_docker_with_timestamp(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Docker log with timestamp"""
        try:
            timestamp, container_id, message = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_timestamp(timestamp)
            
            # Extract log level
            log_level = self._extract_log_level(message)
            
            # Extract source
            source = container_id
            
            # Extract service
            service = self._extract_service_from_container(container_id)
            
            # Extract metadata
            metadata = {
                "container_id": container_id,
                "container_name": self._extract_container_name(container_id),
                "image": self._extract_image_from_message(message),
                "tag": self._extract_tag_from_message(message),
                "format": "docker_timestamp"
            }
            
            # Try to parse message as JSON
            json_data = self._try_parse_json(message)
            if json_data:
                metadata.update(json_data)
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": parsed_timestamp,
                "level": log_level,
                "message": message,
                "source": source,
                "service": service,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.debug(f"Error parsing Docker with timestamp: {e}")
            return None
    
    def _parse_docker_simple(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Docker log without timestamp"""
        try:
            container_id, message = match.groups()
            
            # Extract timestamp from message
            timestamp = self._extract_timestamp_from_message(message)
            
            # Extract log level
            log_level = self._extract_log_level(message)
            
            # Extract source
            source = container_id
            
            # Extract service
            service = self._extract_service_from_container(container_id)
            
            # Extract metadata
            metadata = {
                "container_id": container_id,
                "container_name": self._extract_container_name(container_id),
                "image": self._extract_image_from_message(message),
                "tag": self._extract_tag_from_message(message),
                "format": "docker_simple"
            }
            
            # Try to parse message as JSON
            json_data = self._try_parse_json(message)
            if json_data:
                metadata.update(json_data)
            
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
            
        except Exception as e:
            logger.debug(f"Error parsing Docker simple: {e}")
            return None
    
    def _parse_generic_docker_log(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse generic Docker log line"""
        try:
            # Try to extract basic information
            timestamp = self._extract_timestamp_from_message(line)
            log_level = self._extract_log_level(line)
            source = self._extract_source_from_message(line)
            service = self._extract_service_from_message(line)
            
            # Extract metadata
            metadata = {
                "format": "generic_docker"
            }
            
            # Try to parse message as JSON
            json_data = self._try_parse_json(line)
            if json_data:
                metadata.update(json_data)
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": timestamp,
                "level": log_level,
                "message": line,
                "source": source,
                "service": service,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.debug(f"Error parsing generic Docker log: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse timestamp to ISO format"""
        try:
            # Try dateutil parser first
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
    
    def _extract_log_level(self, message: str) -> str:
        """Extract log level from message"""
        try:
            message_lower = message.lower()
            
            # Check for explicit log level keywords
            for level_str, level_enum in self.log_levels.items():
                if level_str in message_lower:
                    return level_enum
            
            # Check for common error patterns
            if any(keyword in message_lower for keyword in ["error", "exception", "failed", "failure"]):
                return "ERROR"
            elif any(keyword in message_lower for keyword in ["warning", "warn", "caution"]):
                return "WARNING"
            elif any(keyword in message_lower for keyword in ["info", "information"]):
                return "INFO"
            elif any(keyword in message_lower for keyword in ["debug", "trace"]):
                return "DEBUG"
            elif any(keyword in message_lower for keyword in ["critical", "fatal"]):
                return "CRITICAL"
            
            return "INFO"
            
        except Exception as e:
            logger.debug(f"Error extracting log level: {e}")
            return "INFO"
    
    def _try_parse_json(self, message: str) -> Optional[Dict[str, Any]]:
        """Try to parse message as JSON"""
        try:
            data = json.loads(message)
            if isinstance(data, dict):
                return data
            return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def _extract_service_from_container(self, container_id: str) -> Optional[str]:
        """Extract service from container ID"""
        try:
            # Container ID format: container_name or container_name-tag
            if '-' in container_id:
                parts = container_id.split('-')
                return parts[0]
            return container_id
        except Exception as e:
            logger.debug(f"Error extracting service from container: {e}")
            return None
    
    def _extract_container_name(self, container_id: str) -> Optional[str]:
        """Extract container name from container ID"""
        try:
            # Container ID format: container_name or container_name-tag
            if '-' in container_id:
                parts = container_id.split('-')
                return parts[0]
            return container_id
        except Exception as e:
            logger.debug(f"Error extracting container name: {e}")
            return None
    
    def _extract_image_from_message(self, message: str) -> Optional[str]:
        """Extract image from message content"""
        try:
            # Common image patterns
            patterns = [
                r'image[:\s]+([A-Za-z0-9_.-]+)',
                r'from[:\s]+([A-Za-z0-9_.-]+)',
                r'([A-Za-z0-9_.-]+):[A-Za-z0-9_.-]+',  # image:tag
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting image from message: {e}")
            return None
    
    def _extract_tag_from_message(self, message: str) -> Optional[str]:
        """Extract tag from message content"""
        try:
            # Common tag patterns
            patterns = [
                r'tag[:\s]+([A-Za-z0-9_.-]+)',
                r'([A-Za-z0-9_.-]+):([A-Za-z0-9_.-]+)',  # image:tag
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(1) if len(match.groups()) == 1 else match.group(2)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting tag from message: {e}")
            return None
    
    def _extract_timestamp_from_message(self, message: str) -> Optional[str]:
        """Extract timestamp from message content"""
        try:
            # Common timestamp patterns
            patterns = [
                r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)',
                r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
                r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
                r'(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    timestamp_str = match.group(1)
                    return self._parse_timestamp(timestamp_str)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting timestamp from message: {e}")
            return None
    
    def _extract_source_from_message(self, message: str) -> Optional[str]:
        """Extract source from message content"""
        try:
            # Common source patterns
            patterns = [
                r'\[([A-Za-z0-9_.]+)\]',  # [source]
                r'([A-Za-z0-9_.]+):',  # source:
                r'([A-Za-z0-9_-]+)\s+service',  # source service
                r'([A-Za-z0-9_-]+)\s+app',  # source app
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting source from message: {e}")
            return None
    
    def _extract_service_from_message(self, message: str) -> Optional[str]:
        """Extract service from message content"""
        try:
            # Common service patterns
            patterns = [
                r'\[([A-Za-z0-9_.]+)\]',  # [service]
                r'([A-Za-z0-9_.]+):',  # service:
                r'([A-Za-z0-9_-]+)\s+service',  # service
                r'([A-Za-z0-9_-]+)\s+app',  # app
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting service from message: {e}")
            return None
    
    def parse_batch(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse a batch of Docker log lines"""
        try:
            parsed_entries = []
            
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = self._parse_docker_log_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing Docker log line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Docker log parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing Docker log batch: {e}")
            return []

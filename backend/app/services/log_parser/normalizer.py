"""
Log Normalizer for Loglytics AI
Normalizes different log formats to common schema
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from dateutil import parser as date_parser
from enum import Enum

logger = logging.getLogger(__name__)

class LogLevel(str, Enum):
    """Standardized log levels"""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    EMERGENCY = "EMERGENCY"
    ALERT = "ALERT"
    NOTICE = "NOTICE"

class LogNormalizer:
    """Normalizes different log formats to common schema"""
    
    def __init__(self):
        self.log_level_mapping = self._initialize_log_level_mapping()
        self.timestamp_patterns = self._initialize_timestamp_patterns()
        self.source_patterns = self._initialize_source_patterns()
    
    def _initialize_log_level_mapping(self) -> Dict[str, LogLevel]:
        """Initialize log level mapping from various formats"""
        return {
            # Standard levels
            "trace": LogLevel.TRACE,
            "debug": LogLevel.DEBUG,
            "info": LogLevel.INFO,
            "warn": LogLevel.WARN,
            "warning": LogLevel.WARNING,
            "error": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL,
            "fatal": LogLevel.FATAL,
            "emergency": LogLevel.EMERGENCY,
            "alert": LogLevel.ALERT,
            "notice": LogLevel.NOTICE,
            
            # Numeric levels
            "0": LogLevel.EMERGENCY,
            "1": LogLevel.ALERT,
            "2": LogLevel.CRITICAL,
            "3": LogLevel.ERROR,
            "4": LogLevel.WARNING,
            "5": LogLevel.NOTICE,
            "6": LogLevel.INFO,
            "7": LogLevel.DEBUG,
            
            # Apache levels
            "emerg": LogLevel.EMERGENCY,
            "crit": LogLevel.CRITICAL,
            
            # Windows levels
            "verbose": LogLevel.DEBUG,
            "information": LogLevel.INFO,
            
            # Cloud levels
            "severe": LogLevel.CRITICAL,
            "warning": LogLevel.WARNING,
            "informational": LogLevel.INFO,
            "verbose": LogLevel.DEBUG
        }
    
    def _initialize_timestamp_patterns(self) -> List[str]:
        """Initialize timestamp parsing patterns"""
        return [
            # ISO 8601 formats
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S%z",
            
            # Common formats
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S.%f%z",
            "%Y-%m-%d %H:%M:%S%z",
            
            # Apache/Nginx formats
            "%d/%b/%Y:%H:%M:%S %z",
            "%d/%b/%Y:%H:%M:%S",
            
            # Windows formats
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
            
            # Syslog formats
            "%b %d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            
            # Docker formats
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
            
            # Kubernetes formats
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ"
        ]
    
    def _initialize_source_patterns(self) -> List[re.Pattern]:
        """Initialize source extraction patterns"""
        return [
            # File:line patterns
            re.compile(r'([^:]+):(\d+)'),
            re.compile(r'([^:]+):(\d+):(\d+)'),
            
            # Class.method patterns
            re.compile(r'([A-Za-z0-9_.]+)\.([A-Za-z0-9_]+)'),
            
            # Service patterns
            re.compile(r'([A-Za-z0-9_-]+)'),
            
            # Container patterns
            re.compile(r'([A-Za-z0-9_-]+)/([A-Za-z0-9_-]+)'),
            
            # Pod patterns
            re.compile(r'([A-Za-z0-9_-]+)-([A-Za-z0-9_-]+)')
        ]
    
    def normalize(self, parsed_data: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """
        Normalize parsed log data to common schema
        
        Args:
            parsed_data: Parsed log data
            format_type: Original log format
            
        Returns:
            Normalized log data
        """
        try:
            normalized = {
                "timestamp": self._normalize_timestamp(parsed_data, format_type),
                "log_level": self._normalize_log_level(parsed_data, format_type),
                "message": self._normalize_message(parsed_data, format_type),
                "source": self._normalize_source(parsed_data, format_type),
                "service": self._normalize_service(parsed_data, format_type),
                "metadata": self._normalize_metadata(parsed_data, format_type)
            }
            
            # Remove None values
            normalized = {k: v for k, v in normalized.items() if v is not None}
            
            return normalized
            
        except Exception as e:
            logger.error(f"Error normalizing log data: {e}")
            return {
                "timestamp": None,
                "log_level": LogLevel.INFO,
                "message": str(parsed_data),
                "source": None,
                "service": None,
                "metadata": {"error": str(e), "original_data": parsed_data}
            }
    
    def _normalize_timestamp(self, parsed_data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Normalize timestamp to ISO 8601 format"""
        try:
            # Try different timestamp field names
            timestamp_fields = ["timestamp", "time", "@timestamp", "datetime", "date", "ts"]
            
            for field in timestamp_fields:
                if field in parsed_data and parsed_data[field]:
                    timestamp = parsed_data[field]
                    return self._parse_timestamp(timestamp)
            
            # Try to extract timestamp from message
            if "message" in parsed_data:
                timestamp = self._extract_timestamp_from_message(parsed_data["message"])
                if timestamp:
                    return timestamp
            
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing timestamp: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: Union[str, datetime]) -> Optional[str]:
        """Parse timestamp to ISO 8601 format"""
        try:
            if isinstance(timestamp, datetime):
                return timestamp.isoformat() + "Z"
            
            if isinstance(timestamp, str):
                # Try dateutil parser first
                try:
                    parsed = date_parser.parse(timestamp)
                    return parsed.isoformat() + "Z"
                except (ValueError, TypeError):
                    pass
                
                # Try specific patterns
                for pattern in self.timestamp_patterns:
                    try:
                        parsed = datetime.strptime(timestamp, pattern)
                        return parsed.isoformat() + "Z"
                    except ValueError:
                        continue
                
                # Try regex patterns for complex formats
                timestamp = self._parse_complex_timestamp(timestamp)
                if timestamp:
                    return timestamp
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing timestamp: {e}")
            return None
    
    def _parse_complex_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse complex timestamp formats"""
        try:
            # Apache/Nginx format: 25/Dec/2023:10:30:45 +0000
            apache_pattern = re.compile(r'(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})\s+([+-]\d{4})')
            match = apache_pattern.match(timestamp)
            if match:
                day, month, year, hour, minute, second, tz = match.groups()
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                month_num = month_map.get(month, '01')
                iso_timestamp = f"{year}-{month_num}-{day}T{hour}:{minute}:{second}{tz}"
                return iso_timestamp
            
            # Syslog format: Dec 25 10:30:45
            syslog_pattern = re.compile(r'([A-Za-z]{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})')
            match = syslog_pattern.match(timestamp)
            if match:
                month, day, hour, minute, second = match.groups()
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                month_num = month_map.get(month, '01')
                current_year = datetime.now().year
                iso_timestamp = f"{current_year}-{month_num}-{day.zfill(2)}T{hour}:{minute}:{second}Z"
                return iso_timestamp
            
            return None
            
        except Exception as e:
            logger.error(f"Error parsing complex timestamp: {e}")
            return None
    
    def _extract_timestamp_from_message(self, message: str) -> Optional[str]:
        """Extract timestamp from message content"""
        try:
            # Common timestamp patterns in messages
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
            logger.error(f"Error extracting timestamp from message: {e}")
            return None
    
    def _normalize_log_level(self, parsed_data: Dict[str, Any], format_type: str) -> LogLevel:
        """Normalize log level to standard enum"""
        try:
            # Try different log level field names
            level_fields = ["level", "severity", "log_level", "priority", "event_level"]
            
            for field in level_fields:
                if field in parsed_data and parsed_data[field]:
                    level = str(parsed_data[field]).lower().strip()
                    if level in self.log_level_mapping:
                        return self.log_level_mapping[level]
            
            # Try to extract log level from message
            if "message" in parsed_data:
                level = self._extract_log_level_from_message(parsed_data["message"])
                if level:
                    return level
            
            # Default to INFO if no level found
            return LogLevel.INFO
            
        except Exception as e:
            logger.error(f"Error normalizing log level: {e}")
            return LogLevel.INFO
    
    def _extract_log_level_from_message(self, message: str) -> Optional[LogLevel]:
        """Extract log level from message content"""
        try:
            message_lower = message.lower()
            
            # Check for log level keywords
            for level_str, level_enum in self.log_level_mapping.items():
                if level_str in message_lower:
                    return level_enum
            
            # Check for common error patterns
            if any(keyword in message_lower for keyword in ["error", "exception", "failed", "failure"]):
                return LogLevel.ERROR
            
            if any(keyword in message_lower for keyword in ["warning", "warn", "caution"]):
                return LogLevel.WARNING
            
            if any(keyword in message_lower for keyword in ["info", "information"]):
                return LogLevel.INFO
            
            if any(keyword in message_lower for keyword in ["debug", "trace"]):
                return LogLevel.DEBUG
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting log level from message: {e}")
            return None
    
    def _normalize_message(self, parsed_data: Dict[str, Any], format_type: str) -> str:
        """Normalize message content"""
        try:
            # Try different message field names
            message_fields = ["message", "msg", "text", "content", "body", "description"]
            
            for field in message_fields:
                if field in parsed_data and parsed_data[field]:
                    message = str(parsed_data[field]).strip()
                    if message:
                        return message
            
            # If no message field found, use the entire parsed data as message
            return json.dumps(parsed_data, default=str)
            
        except Exception as e:
            logger.error(f"Error normalizing message: {e}")
            return str(parsed_data)
    
    def _normalize_source(self, parsed_data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Normalize source information"""
        try:
            # Try different source field names
            source_fields = ["source", "logger", "component", "module", "class", "file", "function"]
            
            for field in source_fields:
                if field in parsed_data and parsed_data[field]:
                    source = str(parsed_data[field]).strip()
                    if source:
                        return self._extract_source_info(source)
            
            # Try to extract source from message
            if "message" in parsed_data:
                source = self._extract_source_from_message(parsed_data["message"])
                if source:
                    return source
            
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing source: {e}")
            return None
    
    def _extract_source_info(self, source: str) -> str:
        """Extract source information from source string"""
        try:
            # Try different source patterns
            for pattern in self.source_patterns:
                match = pattern.search(source)
                if match:
                    return match.group(0)
            
            return source
            
        except Exception as e:
            logger.error(f"Error extracting source info: {e}")
            return source
    
    def _extract_source_from_message(self, message: str) -> Optional[str]:
        """Extract source from message content"""
        try:
            # Common source patterns in messages
            patterns = [
                r'([A-Za-z0-9_.]+):(\d+)',  # file:line
                r'([A-Za-z0-9_.]+)\.([A-Za-z0-9_]+)',  # class.method
                r'\[([A-Za-z0-9_.]+)\]',  # [source]
                r'([A-Za-z0-9_-]+):',  # source:
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(0)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting source from message: {e}")
            return None
    
    def _normalize_service(self, parsed_data: Dict[str, Any], format_type: str) -> Optional[str]:
        """Normalize service information"""
        try:
            # Try different service field names
            service_fields = ["service", "app", "application", "microservice", "container", "pod", "namespace"]
            
            for field in service_fields:
                if field in parsed_data and parsed_data[field]:
                    service = str(parsed_data[field]).strip()
                    if service:
                        return service
            
            # Try to extract service from source
            if "source" in parsed_data:
                service = self._extract_service_from_source(parsed_data["source"])
                if service:
                    return service
            
            # Try to extract service from message
            if "message" in parsed_data:
                service = self._extract_service_from_message(parsed_data["message"])
                if service:
                    return service
            
            return None
            
        except Exception as e:
            logger.error(f"Error normalizing service: {e}")
            return None
    
    def _extract_service_from_source(self, source: str) -> Optional[str]:
        """Extract service from source information"""
        try:
            # Common service patterns in source
            patterns = [
                r'([A-Za-z0-9_-]+)-service',
                r'([A-Za-z0-9_-]+)-app',
                r'([A-Za-z0-9_-]+)-api',
                r'([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)',  # namespace.service
            ]
            
            for pattern in patterns:
                match = re.search(pattern, source)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting service from source: {e}")
            return None
    
    def _extract_service_from_message(self, message: str) -> Optional[str]:
        """Extract service from message content"""
        try:
            # Common service patterns in messages
            patterns = [
                r'\[([A-Za-z0-9_-]+)\]',  # [service]
                r'([A-Za-z0-9_-]+):',  # service:
                r'([A-Za-z0-9_-]+)\s+service',
                r'([A-Za-z0-9_-]+)\s+app',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting service from message: {e}")
            return None
    
    def _normalize_metadata(self, parsed_data: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Normalize metadata information"""
        try:
            metadata = {}
            
            # Copy format-specific fields to metadata
            format_specific_fields = {
                LogFormat.JSON: ["logger", "thread", "correlation_id", "request_id", "user_id"],
                LogFormat.SYSLOG: ["facility", "severity", "hostname", "app_name", "proc_id", "msg_id"],
                LogFormat.APACHE_ACCESS: ["remote_ip", "remote_user", "request", "status", "bytes", "referer", "user_agent"],
                LogFormat.APACHE_ERROR: ["client", "server", "request", "error", "pid", "tid"],
                LogFormat.NGINX_ACCESS: ["remote_ip", "remote_user", "request", "status", "bytes", "referer", "user_agent", "upstream"],
                LogFormat.NGINX_ERROR: ["client", "server", "request", "error", "pid", "tid"],
                LogFormat.DOCKER: ["container_id", "container_name", "image", "tag"],
                LogFormat.KUBERNETES: ["pod", "namespace", "container", "node", "cluster"],
                LogFormat.AWS_CLOUDWATCH: ["log_group", "log_stream", "event_id", "aws_region"],
                LogFormat.AZURE_MONITOR: ["resource_id", "operation_name", "category", "tenant_id"],
                LogFormat.GCP_CLOUD_LOGGING: ["resource", "labels", "operation", "trace", "span_id"],
                LogFormat.WINDOWS_EVENT: ["event_id", "event_source", "event_category", "event_type", "computer"],
                LogFormat.GENERIC: ["raw_data", "format_detected"]
            }
            
            # Get fields for current format
            fields_to_include = format_specific_fields.get(format_type, [])
            
            # Add format-specific fields to metadata
            for field in fields_to_include:
                if field in parsed_data and parsed_data[field] is not None:
                    metadata[field] = parsed_data[field]
            
            # Add format information
            metadata["original_format"] = format_type
            
            # Add any remaining fields that weren't normalized
            normalized_fields = ["timestamp", "log_level", "message", "source", "service"]
            for key, value in parsed_data.items():
                if key not in normalized_fields and key not in metadata:
                    metadata[key] = value
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error normalizing metadata: {e}")
            return {"error": str(e), "original_data": parsed_data}
    
    def normalize_batch(self, parsed_data_list: List[Dict[str, Any]], format_type: str) -> List[Dict[str, Any]]:
        """Normalize a batch of parsed log data"""
        try:
            normalized_list = []
            
            for parsed_data in parsed_data_list:
                normalized = self.normalize(parsed_data, format_type)
                normalized_list.append(normalized)
            
            return normalized_list
            
        except Exception as e:
            logger.error(f"Error normalizing batch: {e}")
            return []
    
    def get_normalization_stats(self, normalized_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about normalization process"""
        try:
            if not normalized_data_list:
                return {}
            
            stats = {
                "total_entries": len(normalized_data_list),
                "entries_with_timestamp": sum(1 for entry in normalized_data_list if entry.get("timestamp")),
                "entries_with_log_level": sum(1 for entry in normalized_data_list if entry.get("log_level")),
                "entries_with_source": sum(1 for entry in normalized_data_list if entry.get("source")),
                "entries_with_service": sum(1 for entry in normalized_data_list if entry.get("service")),
                "log_level_distribution": {},
                "service_distribution": {},
                "source_distribution": {}
            }
            
            # Count log level distribution
            for entry in normalized_data_list:
                log_level = entry.get("log_level")
                if log_level:
                    stats["log_level_distribution"][log_level] = stats["log_level_distribution"].get(log_level, 0) + 1
            
            # Count service distribution
            for entry in normalized_data_list:
                service = entry.get("service")
                if service:
                    stats["service_distribution"][service] = stats["service_distribution"].get(service, 0) + 1
            
            # Count source distribution
            for entry in normalized_data_list:
                source = entry.get("source")
                if source:
                    stats["source_distribution"][source] = stats["source_distribution"].get(source, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting normalization stats: {e}")
            return {}

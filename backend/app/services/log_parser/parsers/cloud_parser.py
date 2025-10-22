"""
Cloud Log Parser for Loglytics AI
Parses AWS CloudWatch, Azure Monitor, and GCP Cloud Logging
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class CloudLogParser:
    """Parser for cloud log formats (AWS, Azure, GCP)"""
    
    def __init__(self):
        # AWS CloudWatch Logs format
        self.aws_cloudwatch_pattern = re.compile(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(\S+)\s+(.+)$'
        )
        
        # Azure Monitor Logs format
        self.azure_monitor_pattern = re.compile(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'
        )
        
        # GCP Cloud Logging format
        self.gcp_cloud_logging_pattern = re.compile(
            r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(.+)$'
        )
        
        # Cloud-specific indicators
        self.aws_indicators = ["aws", "cloudwatch", "lambda", "ec2", "rds", "s3", "dynamodb", "sqs", "sns"]
        self.azure_indicators = ["azure", "monitor", "appservice", "function", "storage", "cosmosdb", "servicebus"]
        self.gcp_indicators = ["gcp", "google", "cloud", "gke", "cloudrun", "bigquery", "pubsub", "firestore"]
        
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
        Parse cloud log content
        
        Args:
            content: Cloud log content
            
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
                    entry = self._parse_cloud_log_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing cloud log line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Cloud log parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            logger.info(f"Parsed {len(parsed_entries)} cloud log entries")
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing cloud log content: {e}")
            return []
    
    def _parse_cloud_log_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single cloud log line"""
        try:
            # Try AWS CloudWatch format
            match = self.aws_cloudwatch_pattern.match(line.strip())
            if match:
                return self._parse_aws_cloudwatch(match, line, line_num)
            
            # Try Azure Monitor format
            match = self.azure_monitor_pattern.match(line.strip())
            if match:
                return self._parse_azure_monitor(match, line, line_num)
            
            # Try GCP Cloud Logging format
            match = self.gcp_cloud_logging_pattern.match(line.strip())
            if match:
                return self._parse_gcp_cloud_logging(match, line, line_num)
            
            # Try to parse as generic cloud log
            return self._parse_generic_cloud_log(line, line_num)
            
        except Exception as e:
            logger.debug(f"Error parsing cloud log line {line_num}: {e}")
            return None
    
    def _parse_aws_cloudwatch(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse AWS CloudWatch log format"""
        try:
            timestamp, log_group, log_stream, message = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_timestamp(timestamp)
            
            # Extract log level
            log_level = self._extract_log_level(message)
            
            # Extract source
            source = log_stream
            
            # Extract service
            service = log_group
            
            # Extract metadata
            metadata = {
                "log_group": log_group,
                "log_stream": log_stream,
                "aws_region": self._extract_aws_region(log_group),
                "aws_service": self._extract_aws_service(log_group),
                "format": "aws_cloudwatch"
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
            logger.debug(f"Error parsing AWS CloudWatch format: {e}")
            return None
    
    def _parse_azure_monitor(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Azure Monitor log format"""
        try:
            timestamp, resource_id, message = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_timestamp(timestamp)
            
            # Extract log level
            log_level = self._extract_log_level(message)
            
            # Extract source
            source = self._extract_azure_source(resource_id)
            
            # Extract service
            service = self._extract_azure_service(resource_id)
            
            # Extract metadata
            metadata = {
                "resource_id": resource_id,
                "azure_region": self._extract_azure_region(resource_id),
                "azure_service": self._extract_azure_service(resource_id),
                "tenant_id": self._extract_azure_tenant(resource_id),
                "format": "azure_monitor"
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
            logger.debug(f"Error parsing Azure Monitor format: {e}")
            return None
    
    def _parse_gcp_cloud_logging(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse GCP Cloud Logging format"""
        try:
            timestamp, resource, message = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_timestamp(timestamp)
            
            # Extract log level
            log_level = self._extract_log_level(message)
            
            # Extract source
            source = self._extract_gcp_source(resource)
            
            # Extract service
            service = self._extract_gcp_service(resource)
            
            # Extract metadata
            metadata = {
                "resource": resource,
                "gcp_project": self._extract_gcp_project(resource),
                "gcp_service": self._extract_gcp_service(resource),
                "gcp_region": self._extract_gcp_region(resource),
                "format": "gcp_cloud_logging"
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
            logger.debug(f"Error parsing GCP Cloud Logging format: {e}")
            return None
    
    def _parse_generic_cloud_log(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse generic cloud log line"""
        try:
            # Try to extract basic information
            timestamp = self._extract_timestamp_from_message(line)
            log_level = self._extract_log_level(line)
            source = self._extract_source_from_message(line)
            service = self._extract_service_from_message(line)
            
            # Determine cloud provider
            cloud_provider = self._detect_cloud_provider(line)
            
            # Extract metadata
            metadata = {
                "cloud_provider": cloud_provider,
                "format": "generic_cloud"
            }
            
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
            logger.debug(f"Error parsing generic cloud log: {e}")
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
    
    def _extract_aws_region(self, log_group: str) -> Optional[str]:
        """Extract AWS region from log group"""
        try:
            # Common AWS region patterns
            regions = ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1", "ap-northeast-1"]
            for region in regions:
                if region in log_group:
                    return region
            return None
        except Exception as e:
            logger.debug(f"Error extracting AWS region: {e}")
            return None
    
    def _extract_aws_service(self, log_group: str) -> Optional[str]:
        """Extract AWS service from log group"""
        try:
            for service in self.aws_indicators:
                if service in log_group.lower():
                    return service
            return None
        except Exception as e:
            logger.debug(f"Error extracting AWS service: {e}")
            return None
    
    def _extract_azure_region(self, resource_id: str) -> Optional[str]:
        """Extract Azure region from resource ID"""
        try:
            # Azure resource ID format: /subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/{resource-provider}/{resource-type}/{resource-name}
            parts = resource_id.split('/')
            if len(parts) > 4:
                return parts[4]  # Usually the resource group contains region info
            return None
        except Exception as e:
            logger.debug(f"Error extracting Azure region: {e}")
            return None
    
    def _extract_azure_service(self, resource_id: str) -> Optional[str]:
        """Extract Azure service from resource ID"""
        try:
            for service in self.azure_indicators:
                if service in resource_id.lower():
                    return service
            return None
        except Exception as e:
            logger.debug(f"Error extracting Azure service: {e}")
            return None
    
    def _extract_azure_tenant(self, resource_id: str) -> Optional[str]:
        """Extract Azure tenant ID from resource ID"""
        try:
            # Azure resource ID format: /subscriptions/{subscription-id}/...
            parts = resource_id.split('/')
            if len(parts) > 2:
                return parts[2]  # Subscription ID
            return None
        except Exception as e:
            logger.debug(f"Error extracting Azure tenant: {e}")
            return None
    
    def _extract_azure_source(self, resource_id: str) -> Optional[str]:
        """Extract Azure source from resource ID"""
        try:
            # Extract resource name from resource ID
            parts = resource_id.split('/')
            if len(parts) > 0:
                return parts[-1]  # Last part is usually the resource name
            return None
        except Exception as e:
            logger.debug(f"Error extracting Azure source: {e}")
            return None
    
    def _extract_gcp_project(self, resource: str) -> Optional[str]:
        """Extract GCP project from resource"""
        try:
            # GCP resource format: projects/{project-id}/...
            if resource.startswith("projects/"):
                parts = resource.split('/')
                if len(parts) > 1:
                    return parts[1]
            return None
        except Exception as e:
            logger.debug(f"Error extracting GCP project: {e}")
            return None
    
    def _extract_gcp_service(self, resource: str) -> Optional[str]:
        """Extract GCP service from resource"""
        try:
            for service in self.gcp_indicators:
                if service in resource.lower():
                    return service
            return None
        except Exception as e:
            logger.debug(f"Error extracting GCP service: {e}")
            return None
    
    def _extract_gcp_region(self, resource: str) -> Optional[str]:
        """Extract GCP region from resource"""
        try:
            # Common GCP regions
            regions = ["us-central1", "us-east1", "us-west1", "europe-west1", "asia-east1"]
            for region in regions:
                if region in resource:
                    return region
            return None
        except Exception as e:
            logger.debug(f"Error extracting GCP region: {e}")
            return None
    
    def _extract_gcp_source(self, resource: str) -> Optional[str]:
        """Extract GCP source from resource"""
        try:
            # Extract resource name from resource
            parts = resource.split('/')
            if len(parts) > 0:
                return parts[-1]  # Last part is usually the resource name
            return None
        except Exception as e:
            logger.debug(f"Error extracting GCP source: {e}")
            return None
    
    def _detect_cloud_provider(self, line: str) -> str:
        """Detect cloud provider from line content"""
        try:
            line_lower = line.lower()
            
            if any(indicator in line_lower for indicator in self.aws_indicators):
                return "aws"
            elif any(indicator in line_lower for indicator in self.azure_indicators):
                return "azure"
            elif any(indicator in line_lower for indicator in self.gcp_indicators):
                return "gcp"
            else:
                return "unknown"
                
        except Exception as e:
            logger.debug(f"Error detecting cloud provider: {e}")
            return "unknown"
    
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
        """Parse a batch of cloud log lines"""
        try:
            parsed_entries = []
            
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = self._parse_cloud_log_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing cloud log line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Cloud log parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing cloud log batch: {e}")
            return []

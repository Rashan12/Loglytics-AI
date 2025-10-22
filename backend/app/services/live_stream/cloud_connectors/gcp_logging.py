import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.cloud import logging as gcp_logging
from google.oauth2 import service_account
from google.api_core import exceptions as gcp_exceptions

logger = logging.getLogger(__name__)

class GCPLoggingConnector:
    """
    Google Cloud Logging connector for real-time log streaming
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.project_id = config.get("project_id")
        self.log_name = config.get("log_name", "")
        self.resource_type = config.get("resource_type", "")
        self.credentials_path = config.get("credentials_path")
        self.credentials_json = config.get("credentials_json")
        self._last_timestamp = None
        
        # Initialize GCP client
        self._init_client()
    
    def _init_client(self):
        """Initialize Google Cloud Logging client"""
        try:
            # Use service account credentials if provided
            if self.credentials_json:
                # Parse JSON credentials
                if isinstance(self.credentials_json, str):
                    credentials_info = json.loads(self.credentials_json)
                else:
                    credentials_info = self.credentials_json
                
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info
                )
            elif self.credentials_path:
                # Use credentials file
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
            else:
                # Use default credentials (Application Default Credentials)
                credentials = None
            
            self.client = gcp_logging.Client(
                project=self.project_id,
                credentials=credentials
            )
            
            logger.info(f"Initialized GCP Logging client for project {self.project_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize GCP client: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """Test the connection to Google Cloud Logging"""
        try:
            # Test by listing log entries
            filter_str = f'resource.type="gce_instance"'
            if self.log_name:
                filter_str += f' AND logName="{self.log_name}"'
            
            # Query for recent entries
            entries = self.client.list_entries(
                filter_=filter_str,
                max_results=1,
                order_by=gcp_logging.DESCENDING
            )
            
            # Try to get at least one entry
            entry_list = list(entries)
            
            logger.info(f"Successfully connected to GCP project {self.project_id}")
            return True
            
        except gcp_exceptions.PermissionDenied:
            logger.error("Permission denied to Google Cloud Logging")
            return False
        except gcp_exceptions.NotFound:
            logger.error(f"Project {self.project_id} not found")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def fetch_logs(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch new logs from Google Cloud Logging"""
        try:
            # Build filter string
            filter_parts = []
            
            # Time filter
            if since:
                time_str = since.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                filter_parts.append(f'timestamp>="{time_str}"')
            else:
                # Default to last hour
                since = datetime.utcnow() - timedelta(hours=1)
                time_str = since.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                filter_parts.append(f'timestamp>="{time_str}"')
            
            # Log name filter
            if self.log_name:
                filter_parts.append(f'logName="{self.log_name}"')
            
            # Resource type filter
            if self.resource_type:
                filter_parts.append(f'resource.type="{self.resource_type}"')
            
            # Combine filters
            filter_str = ' AND '.join(filter_parts)
            
            # Query log entries
            entries = self.client.list_entries(
                filter_=filter_str,
                max_results=1000,
                order_by=gcp_logging.DESCENDING
            )
            
            # Parse entries
            logs = []
            for entry in entries:
                log_entry = self._parse_log_entry(entry)
                if log_entry:
                    logs.append(log_entry)
            
            # Sort by timestamp
            logs.sort(key=lambda x: x.get("timestamp", datetime.min))
            
            # Update last timestamp
            if logs:
                self._last_timestamp = max(log.get("timestamp", datetime.min) for log in logs)
            
            logger.debug(f"Fetched {len(logs)} logs from GCP project {self.project_id}")
            return logs
            
        except Exception as e:
            logger.error(f"Failed to fetch logs: {str(e)}")
            return []
    
    def _parse_log_entry(self, entry) -> Optional[Dict[str, Any]]:
        """Parse a GCP log entry into our standard format"""
        try:
            # Extract timestamp
            timestamp = entry.timestamp
            if hasattr(timestamp, 'to_pydatetime'):
                timestamp = timestamp.to_pydatetime()
            elif isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if not timestamp:
                timestamp = datetime.utcnow()
            
            # Extract message
            message = self._extract_message(entry)
            
            # Extract log level
            log_level = self._extract_log_level(entry)
            
            # Extract source
            source = self._extract_source(entry)
            
            # Build metadata
            metadata = {
                "cloud_provider": "gcp",
                "project_id": self.project_id,
                "log_name": entry.log_name,
                "resource_type": entry.resource.type if entry.resource else None,
                "labels": dict(entry.labels) if entry.labels else {},
                "severity": entry.severity,
                "insert_id": entry.insert_id,
                "http_request": dict(entry.http_request) if entry.http_request else None,
                "operation": dict(entry.operation) if entry.operation else None,
                "trace": entry.trace,
                "span_id": entry.span_id
            }
            
            return {
                "timestamp": timestamp,
                "log_level": log_level,
                "message": message,
                "source": source,
                "metadata": metadata,
                "raw_content": str(entry.payload) if hasattr(entry, 'payload') else message
            }
            
        except Exception as e:
            logger.error(f"Failed to parse log entry: {str(e)}")
            return None
    
    def _extract_message(self, entry) -> str:
        """Extract message from GCP log entry"""
        # Try payload first
        if hasattr(entry, 'payload') and entry.payload:
            if isinstance(entry.payload, dict):
                # Try common message fields
                message_fields = ['message', 'msg', 'text', 'description', 'error']
                for field in message_fields:
                    if field in entry.payload:
                        return str(entry.payload[field])
                
                # If payload is a dict, convert to JSON
                return json.dumps(entry.payload)
            else:
                return str(entry.payload)
        
        # Fallback to empty string
        return "No message available"
    
    def _extract_log_level(self, entry) -> str:
        """Extract log level from GCP log entry"""
        # GCP severity levels
        severity = entry.severity
        if severity:
            severity_map = {
                'DEBUG': 'DEBUG',
                'INFO': 'INFO',
                'NOTICE': 'INFO',
                'WARNING': 'WARN',
                'ERROR': 'ERROR',
                'CRITICAL': 'CRITICAL',
                'ALERT': 'CRITICAL',
                'EMERGENCY': 'CRITICAL'
            }
            return severity_map.get(severity, 'INFO')
        
        # Try to infer from message content
        message = str(entry.payload).upper() if hasattr(entry, 'payload') else ""
        if any(level in message for level in ['CRITICAL', 'FATAL', 'EMERGENCY']):
            return "CRITICAL"
        elif 'ERROR' in message:
            return "ERROR"
        elif any(level in message for level in ['WARN', 'WARNING']):
            return "WARN"
        elif 'DEBUG' in message:
            return "DEBUG"
        else:
            return "INFO"
    
    def _extract_source(self, entry) -> str:
        """Extract source from GCP log entry"""
        # Try resource labels
        if entry.resource and entry.resource.labels:
            labels = entry.resource.labels
            # Common source fields
            source_fields = ['instance_name', 'service_name', 'module_name', 'function_name']
            for field in source_fields:
                if field in labels:
                    return labels[field]
        
        # Try log name
        if entry.log_name:
            # Extract service name from log name
            # Format: projects/PROJECT_ID/logs/LOG_NAME
            parts = entry.log_name.split('/')
            if len(parts) >= 4:
                return parts[-1]  # Last part is usually the service name
        
        # Try labels
        if entry.labels:
            labels = dict(entry.labels)
            if 'service' in labels:
                return labels['service']
            elif 'module' in labels:
                return labels['module']
        
        # Default fallback
        return "gcp-service"
    
    async def close(self):
        """Close the connection and cleanup resources"""
        try:
            if self.client:
                # GCP clients don't need explicit closing
                self.client = None
            logger.info("GCP Logging connector closed")
        except Exception as e:
            logger.error(f"Error closing GCP connector: {str(e)}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            "provider": "gcp",
            "project_id": self.project_id,
            "log_name": self.log_name,
            "resource_type": self.resource_type,
            "last_timestamp": self._last_timestamp.isoformat() if self._last_timestamp else None
        }

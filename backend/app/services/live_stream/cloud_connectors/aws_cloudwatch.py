import boto3
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

class AWSCloudWatchConnector:
    """
    AWS CloudWatch Logs connector for real-time log streaming
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logs_client = None
        self.log_group = config.get("log_group")
        self.log_streams = config.get("log_streams", [])
        self.region = config.get("region", "us-east-1")
        self._last_token = None
        
        # Initialize AWS client
        self._init_client()
    
    def _init_client(self):
        """Initialize AWS CloudWatch Logs client"""
        try:
            # Use provided credentials or default credential chain
            if "access_key_id" in self.config and "secret_access_key" in self.config:
                self.logs_client = boto3.client(
                    'logs',
                    region_name=self.region,
                    aws_access_key_id=self.config["access_key_id"],
                    aws_secret_access_key=self.config["secret_access_key"]
                )
            else:
                # Use default credential chain (IAM role, environment variables, etc.)
                self.logs_client = boto3.client(
                    'logs',
                    region_name=self.region
                )
            
            logger.info(f"Initialized AWS CloudWatch client for region {self.region}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize AWS client: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """Test the connection to AWS CloudWatch"""
        try:
            # Test by describing log groups
            response = self.logs_client.describe_log_groups(
                logGroupNamePrefix=self.log_group,
                limit=1
            )
            
            # Check if the log group exists
            log_groups = response.get("logGroups", [])
            if not log_groups:
                logger.error(f"Log group {self.log_group} not found")
                return False
            
            logger.info(f"Successfully connected to log group {self.log_group}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Log group {self.log_group} not found")
            elif error_code == 'AccessDeniedException':
                logger.error("Access denied to CloudWatch Logs")
            else:
                logger.error(f"AWS error: {error_code} - {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def fetch_logs(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch new logs from CloudWatch"""
        try:
            logs = []
            
            # If no specific log streams, get all streams in the log group
            if not self.log_streams:
                log_streams = await self._get_log_streams()
            else:
                log_streams = self.log_streams
            
            # Fetch logs from each stream
            for stream_name in log_streams:
                stream_logs = await self._fetch_stream_logs(stream_name, since)
                logs.extend(stream_logs)
            
            # Sort by timestamp
            logs.sort(key=lambda x: x.get("timestamp", 0))
            
            logger.debug(f"Fetched {len(logs)} logs from {len(log_streams)} streams")
            return logs
            
        except Exception as e:
            logger.error(f"Failed to fetch logs: {str(e)}")
            return []
    
    async def _get_log_streams(self) -> List[str]:
        """Get all log streams in the log group"""
        try:
            response = self.logs_client.describe_log_streams(
                logGroupName=self.log_group,
                orderBy='LastEventTime',
                descending=True,
                limit=50  # Limit to recent streams
            )
            
            return [stream['logStreamName'] for stream in response.get('logStreams', [])]
            
        except ClientError as e:
            logger.error(f"Failed to get log streams: {str(e)}")
            return []
    
    async def _fetch_stream_logs(self, stream_name: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch logs from a specific stream"""
        try:
            # Calculate start time (default to 1 hour ago if not specified)
            if since:
                start_time = int(since.timestamp() * 1000)
            else:
                start_time = int((datetime.utcnow() - timedelta(hours=1)).timestamp() * 1000)
            
            end_time = int(datetime.utcnow().timestamp() * 1000)
            
            # Prepare parameters
            params = {
                'logGroupName': self.log_group,
                'logStreamName': stream_name,
                'startTime': start_time,
                'endTime': end_time,
                'limit': 1000  # Max logs per request
            }
            
            # Add next token if we have one (for pagination)
            if self._last_token:
                params['nextToken'] = self._last_token
            
            response = self.logs_client.get_log_events(**params)
            
            # Process log events
            logs = []
            for event in response.get('events', []):
                log_entry = self._parse_log_event(event, stream_name)
                if log_entry:
                    logs.append(log_entry)
            
            # Update last token for pagination
            self._last_token = response.get('nextForwardToken')
            
            return logs
            
        except ClientError as e:
            logger.error(f"Failed to fetch logs from stream {stream_name}: {str(e)}")
            return []
    
    def _parse_log_event(self, event: Dict[str, Any], stream_name: str) -> Optional[Dict[str, Any]]:
        """Parse a CloudWatch log event into our standard format"""
        try:
            message = event.get('message', '')
            timestamp = event.get('timestamp', 0)
            
            # Convert timestamp from milliseconds to datetime
            log_time = datetime.fromtimestamp(timestamp / 1000)
            
            # Try to parse JSON logs
            try:
                parsed_message = json.loads(message)
                log_level = self._extract_log_level(parsed_message)
                source = parsed_message.get('source', stream_name)
                metadata = parsed_message
            except (json.JSONDecodeError, TypeError):
                # Plain text log
                log_level = self._extract_log_level_from_text(message)
                source = stream_name
                metadata = {"raw_message": message}
            
            return {
                "timestamp": log_time,
                "log_level": log_level,
                "message": message,
                "source": source,
                "metadata": {
                    **metadata,
                    "cloud_provider": "aws",
                    "log_group": self.log_group,
                    "log_stream": stream_name,
                    "event_id": event.get('eventId'),
                    "ingestion_time": event.get('ingestionTime')
                },
                "raw_content": message
            }
            
        except Exception as e:
            logger.error(f"Failed to parse log event: {str(e)}")
            return None
    
    def _extract_log_level(self, parsed_message: Dict[str, Any]) -> str:
        """Extract log level from parsed JSON message"""
        # Common log level fields
        level_fields = ['level', 'log_level', 'severity', 'priority']
        
        for field in level_fields:
            if field in parsed_message:
                level = str(parsed_message[field]).upper()
                if level in ['DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL']:
                    return level
        
        # Default to INFO if no level found
        return "INFO"
    
    def _extract_log_level_from_text(self, message: str) -> str:
        """Extract log level from plain text message"""
        message_upper = message.upper()
        
        if any(level in message_upper for level in ['CRITICAL', 'FATAL']):
            return "CRITICAL"
        elif 'ERROR' in message_upper:
            return "ERROR"
        elif any(level in message_upper for level in ['WARN', 'WARNING']):
            return "WARN"
        elif 'DEBUG' in message_upper:
            return "DEBUG"
        else:
            return "INFO"
    
    async def close(self):
        """Close the connection and cleanup resources"""
        try:
            if self.logs_client:
                # AWS clients don't need explicit closing
                self.logs_client = None
            logger.info("AWS CloudWatch connector closed")
        except Exception as e:
            logger.error(f"Error closing AWS connector: {str(e)}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            "provider": "aws",
            "log_group": self.log_group,
            "log_streams": self.log_streams,
            "region": self.region,
            "last_token": self._last_token
        }

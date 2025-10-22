import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from azure.monitor.query import LogsQueryClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

logger = logging.getLogger(__name__)

class AzureMonitorConnector:
    """
    Azure Monitor Log Analytics connector for real-time log streaming
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.workspace_id = config.get("workspace_id")
        self.query = config.get("query", "")
        self.tenant_id = config.get("tenant_id")
        self.client_id = config.get("client_id")
        self.client_secret = config.get("client_secret")
        self._last_query_time = None
        
        # Initialize Azure client
        self._init_client()
    
    def _init_client(self):
        """Initialize Azure Monitor Logs Query client"""
        try:
            # Use service principal if credentials provided
            if all([self.tenant_id, self.client_id, self.client_secret]):
                credential = ClientSecretCredential(
                    tenant_id=self.tenant_id,
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
            else:
                # Use default credential chain (managed identity, environment variables, etc.)
                credential = DefaultAzureCredential()
            
            self.client = LogsQueryClient(credential)
            logger.info(f"Initialized Azure Monitor client for workspace {self.workspace_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure client: {str(e)}")
            raise
    
    async def test_connection(self) -> bool:
        """Test the connection to Azure Monitor"""
        try:
            # Test with a simple query
            test_query = """
            AppTraces
            | take 1
            | project TimeGenerated, Message
            """
            
            response = self.client.query_workspace(
                workspace_id=self.workspace_id,
                query=test_query,
                timespan=timedelta(minutes=5)
            )
            
            # Check if we got a response
            if response and response.tables:
                logger.info(f"Successfully connected to workspace {self.workspace_id}")
                return True
            else:
                logger.error(f"No data found in workspace {self.workspace_id}")
                return False
                
        except HttpResponseError as e:
            logger.error(f"Azure Monitor error: {e.status_code} - {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def fetch_logs(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch new logs from Azure Monitor"""
        try:
            # Build KQL query with time filter
            if since:
                time_filter = f"TimeGenerated > datetime({since.isoformat()})"
            else:
                # Default to last hour
                since = datetime.utcnow() - timedelta(hours=1)
                time_filter = f"TimeGenerated > datetime({since.isoformat()})"
            
            # Combine user query with time filter
            if self.query:
                full_query = f"{self.query} | where {time_filter}"
            else:
                # Default query for common log tables
                full_query = f"""
                union AppTraces, AppExceptions, AppDependencies, AppRequests
                | where {time_filter}
                | order by TimeGenerated desc
                | take 1000
                """
            
            # Execute query
            response = self.client.query_workspace(
                workspace_id=self.workspace_id,
                query=full_query,
                timespan=timedelta(hours=1)  # Query last hour
            )
            
            # Parse results
            logs = []
            if response and response.tables:
                for table in response.tables:
                    table_logs = self._parse_table_results(table)
                    logs.extend(table_logs)
            
            # Sort by timestamp
            logs.sort(key=lambda x: x.get("timestamp", datetime.min))
            
            # Update last query time
            self._last_query_time = datetime.utcnow()
            
            logger.debug(f"Fetched {len(logs)} logs from Azure Monitor")
            return logs
            
        except Exception as e:
            logger.error(f"Failed to fetch logs: {str(e)}")
            return []
    
    def _parse_table_results(self, table) -> List[Dict[str, Any]]:
        """Parse Azure Monitor table results into our standard format"""
        logs = []
        
        try:
            # Get column names
            columns = [col.name for col in table.columns]
            
            # Process each row
            for row in table.rows:
                log_entry = self._parse_log_row(row, columns)
                if log_entry:
                    logs.append(log_entry)
                    
        except Exception as e:
            logger.error(f"Failed to parse table results: {str(e)}")
        
        return logs
    
    def _parse_log_row(self, row: List, columns: List[str]) -> Optional[Dict[str, Any]]:
        """Parse a single log row into our standard format"""
        try:
            # Create row dictionary
            row_dict = dict(zip(columns, row))
            
            # Extract timestamp
            timestamp = row_dict.get('TimeGenerated')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif hasattr(timestamp, 'to_pydatetime'):
                timestamp = timestamp.to_pydatetime()
            
            if not timestamp:
                timestamp = datetime.utcnow()
            
            # Extract message
            message = self._extract_message(row_dict)
            
            # Extract log level
            log_level = self._extract_log_level(row_dict)
            
            # Extract source
            source = self._extract_source(row_dict)
            
            # Build metadata
            metadata = {
                "cloud_provider": "azure",
                "workspace_id": self.workspace_id,
                "table_name": getattr(row_dict, 'table_name', 'unknown'),
                **{k: v for k, v in row_dict.items() if k not in ['TimeGenerated', 'Message', 'Level', 'Source']}
            }
            
            return {
                "timestamp": timestamp,
                "log_level": log_level,
                "message": message,
                "source": source,
                "metadata": metadata,
                "raw_content": str(row_dict)
            }
            
        except Exception as e:
            logger.error(f"Failed to parse log row: {str(e)}")
            return None
    
    def _extract_message(self, row_dict: Dict[str, Any]) -> str:
        """Extract message from log row"""
        # Try common message fields
        message_fields = ['Message', 'Text', 'Description', 'Exception', 'Details']
        
        for field in message_fields:
            if field in row_dict and row_dict[field]:
                return str(row_dict[field])
        
        # Fallback to first string field
        for key, value in row_dict.items():
            if isinstance(value, str) and value.strip():
                return value
        
        return "No message available"
    
    def _extract_log_level(self, row_dict: Dict[str, Any]) -> str:
        """Extract log level from log row"""
        # Try common level fields
        level_fields = ['Level', 'SeverityLevel', 'LogLevel', 'Priority']
        
        for field in level_fields:
            if field in row_dict:
                level = str(row_dict[field]).upper()
                if level in ['DEBUG', 'INFO', 'WARN', 'WARNING', 'ERROR', 'CRITICAL', 'FATAL']:
                    return level
        
        # Try to infer from message content
        message = str(row_dict.get('Message', '')).upper()
        if any(level in message for level in ['CRITICAL', 'FATAL']):
            return "CRITICAL"
        elif 'ERROR' in message:
            return "ERROR"
        elif any(level in message for level in ['WARN', 'WARNING']):
            return "WARN"
        elif 'DEBUG' in message:
            return "DEBUG"
        else:
            return "INFO"
    
    def _extract_source(self, row_dict: Dict[str, Any]) -> str:
        """Extract source from log row"""
        # Try common source fields
        source_fields = ['Source', 'Component', 'Application', 'Service', 'RoleName']
        
        for field in source_fields:
            if field in row_dict and row_dict[field]:
                return str(row_dict[field])
        
        # Fallback to table name or default
        return row_dict.get('table_name', 'azure-monitor')
    
    async def close(self):
        """Close the connection and cleanup resources"""
        try:
            if self.client:
                # Azure clients don't need explicit closing
                self.client = None
            logger.info("Azure Monitor connector closed")
        except Exception as e:
            logger.error(f"Error closing Azure connector: {str(e)}")
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information for debugging"""
        return {
            "provider": "azure",
            "workspace_id": self.workspace_id,
            "query": self.query,
            "tenant_id": self.tenant_id,
            "last_query_time": self._last_query_time.isoformat() if self._last_query_time else None
        }

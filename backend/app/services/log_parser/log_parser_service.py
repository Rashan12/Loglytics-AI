from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
import re
import json
import asyncio
from datetime import datetime
import logging

from app.models.log_file import LogFile
from app.models.log_entry import LogEntry
from app.services.rag.rag_service import RAGService

logger = logging.getLogger(__name__)


class LogParserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag_service = RAGService(db)
        
        # Common log patterns
        self.patterns = {
            'timestamp': [
                r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?',
                r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}',
                r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]'
            ],
            'level': [
                r'\b(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|TRACE)\b',
                r'\[(DEBUG|INFO|WARN|WARNING|ERROR|FATAL|TRACE)\]'
            ],
            'ip_address': [
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'
            ],
            'thread_id': [
                r'\[thread-\d+\]',
                r'\[Thread-\d+\]',
                r'thread-\d+'
            ],
            'session_id': [
                r'session[_-]?id[:\s=]+([a-zA-Z0-9\-_]+)',
                r'sid[:\s=]+([a-zA-Z0-9\-_]+)'
            ],
            'user_id': [
                r'user[_-]?id[:\s=]+([a-zA-Z0-9\-_]+)',
                r'uid[:\s=]+([a-zA-Z0-9\-_]+)'
            ]
        }

    async def process_log_file(self, log_file_id: int):
        """Process a log file and extract log entries"""
        # Use async query
        result = await self.db.execute(
            select(LogFile).where(LogFile.id == log_file_id)
        )
        log_file = result.scalar_one_or_none()
        
        if not log_file:
            logger.error(f"Log file {log_file_id} not found")
            return
        
        try:
            # Update status to processing
            log_file.upload_status = "processing"
            await self.db.commit()
            
            # Read and parse log file - construct path from filename
            # Files are stored in uploads/{project_id}/{filename} or uploads/{filename} for direct uploads
            import os
            if log_file.project_id:
                project_dir = f"uploads/{log_file.project_id}"
                file_path = os.path.join(project_dir, log_file.filename)
            else:
                # Direct uploads without a project are stored directly in uploads/
                file_path = os.path.join("uploads", log_file.filename)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            log_entries = []
            for line_num, line in enumerate(lines, 1):
                parsed_entry = self.parse_log_line(
                    line.strip(), 
                    line_num, 
                    log_file_id, 
                    log_file.project_id if log_file.project_id else None,  # Can be None
                    log_file.user_id
                )
                if parsed_entry:
                    log_entries.append(parsed_entry)
            
            # Batch insert log entries
            if log_entries:
                # Use async bulk insert
                await self.db.run_sync(
                    lambda session: session.bulk_insert_mappings(LogEntry, log_entries)
                )
                await self.db.commit()
                
                # Add to RAG system
                result = await self.db.execute(
                    select(LogEntry).where(LogEntry.log_file_id == log_file_id)
                )
                db_entries = result.scalars().all()
                
                # RAG service add_log_entries might not exist, skip for now
                # await self.rag_service.add_log_entries(db_entries)
            
            # Update log file status
            log_file.upload_status = "completed"
            log_file.is_processed = True
            await self.db.commit()
            
            logger.info(f"Processed {len(log_entries)} log entries from {log_file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing log file {log_file_id}: {str(e)}")
            log_file.upload_status = "failed"
            log_file.processing_error = str(e)
            await self.db.commit()

    def parse_log_line(self, line: str, line_number: int, log_file_id: int, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line and extract structured data"""
        if not line.strip():
            return None
        
        parsed_data = {
            'log_file_id': log_file_id,
            'project_id': project_id,  # Add required project_id
            'user_id': user_id,  # Add required user_id
            'message': line,
            'parsed_data': {}
        }
        
        # Extract timestamp
        timestamp = self.extract_timestamp(line)
        if timestamp:
            parsed_data['timestamp'] = timestamp
            parsed_data['parsed_data']['timestamp'] = timestamp.isoformat()
        else:
            # Use current time if no timestamp found
            parsed_data['timestamp'] = datetime.now()
            parsed_data['parsed_data']['timestamp'] = datetime.now().isoformat()
        
        # Extract log level
        level = self.extract_log_level(line)
        if level:
            parsed_data['level'] = level
            parsed_data['parsed_data']['level'] = level
        
        # Extract IP address
        ip_address = self.extract_ip_address(line)
        if ip_address:
            parsed_data['ip_address'] = ip_address
            parsed_data['parsed_data']['ip_address'] = ip_address
        
        # Extract thread ID
        thread_id = self.extract_thread_id(line)
        if thread_id:
            parsed_data['thread_id'] = thread_id
            parsed_data['parsed_data']['thread_id'] = thread_id
        
        # Extract session ID
        session_id = self.extract_session_id(line)
        if session_id:
            parsed_data['session_id'] = session_id
            parsed_data['parsed_data']['session_id'] = session_id
        
        # Extract user ID
        user_id = self.extract_user_id(line)
        if user_id:
            parsed_data['user_id'] = user_id
            parsed_data['parsed_data']['user_id'] = user_id
        
        # Extract source/component
        source = self.extract_source(line)
        if source:
            parsed_data['source'] = source
            parsed_data['parsed_data']['source'] = source
        
        # Extract user agent
        user_agent = self.extract_user_agent(line)
        if user_agent:
            parsed_data['user_agent'] = user_agent
            parsed_data['parsed_data']['user_agent'] = user_agent
        
        # Store raw content
        parsed_data['raw_content'] = line
        
        # Set log_level if extracted
        if 'level' in parsed_data and parsed_data['level']:
            parsed_data['log_level'] = parsed_data['level']
            del parsed_data['level']
        
        # Store parsed data as JSON in log_metadata
        if 'parsed_data' in parsed_data:
            parsed_data['log_metadata'] = json.dumps(parsed_data.get('parsed_data', {}))
        
        # Remove fields that don't exist in LogEntry model
        fields_to_keep = ['log_file_id', 'project_id', 'user_id', 'timestamp', 'log_level', 'message', 'source', 'log_metadata', 'raw_content']
        parsed_data = {k: v for k, v in parsed_data.items() if k in fields_to_keep}
        
        return parsed_data

    def extract_timestamp(self, line: str) -> Optional[datetime]:
        """Extract timestamp from log line"""
        for pattern in self.patterns['timestamp']:
            match = re.search(pattern, line)
            if match:
                try:
                    timestamp_str = match.group(0)
                    # Try different timestamp formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%S.%f', 
                               '%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S',
                               '%m/%d/%Y %H:%M:%S', '[%Y-%m-%d %H:%M:%S]']:
                        try:
                            if fmt.startswith('['):
                                timestamp_str = timestamp_str.strip('[]')
                            return datetime.strptime(timestamp_str, fmt)
                        except ValueError:
                            continue
                except Exception:
                    continue
        return None

    def extract_log_level(self, line: str) -> Optional[str]:
        """Extract log level from log line"""
        for pattern in self.patterns['level']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                level = match.group(1) if match.groups() else match.group(0)
                # Normalize to uppercase and map variations to valid enum values
                if level:
                    normalized_level = level.upper()
                    # Map WARNING to WARN to match enum
                    if normalized_level == 'WARNING':
                        normalized_level = 'WARN'
                    # Only return valid enum values
                    valid_levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL']
                    if normalized_level in valid_levels:
                        return normalized_level
        return None

    def extract_ip_address(self, line: str) -> Optional[str]:
        """Extract IP address from log line"""
        for pattern in self.patterns['ip_address']:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        return None

    def extract_thread_id(self, line: str) -> Optional[str]:
        """Extract thread ID from log line"""
        for pattern in self.patterns['thread_id']:
            match = re.search(pattern, line)
            if match:
                return match.group(0)
        return None

    def extract_session_id(self, line: str) -> Optional[str]:
        """Extract session ID from log line"""
        for pattern in self.patterns['session_id']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extract_user_id(self, line: str) -> Optional[str]:
        """Extract user ID from log line"""
        for pattern in self.patterns['user_id']:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extract_source(self, line: str) -> Optional[str]:
        """Extract source/component from log line"""
        # Look for common source patterns
        patterns = [
            r'\[([A-Za-z0-9_.-]+)\]',
            r'([A-Za-z0-9_.-]+):\s',
            r'([A-Za-z0-9_.-]+)\s+\['
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return None

    def extract_user_agent(self, line: str) -> Optional[str]:
        """Extract user agent from log line"""
        pattern = r'User-Agent:\s*([^,\s]+)'
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1)
        return None

    async def detect_anomalies(self, log_file_id: int, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Detect anomalies in log entries"""
        log_entries = self.db.query(LogEntry).filter(
            LogEntry.log_file_id == log_file_id
        ).all()
        
        if not log_entries:
            return []
        
        # Simple anomaly detection based on log level frequency
        level_counts = {}
        for entry in log_entries:
            level = entry.level or 'UNKNOWN'
            level_counts[level] = level_counts.get(level, 0) + 1
        
        total_entries = len(log_entries)
        anomalies = []
        
        for entry in log_entries:
            level = entry.level or 'UNKNOWN'
            level_frequency = level_counts[level] / total_entries
            
            # Mark as anomaly if level frequency is below threshold
            if level_frequency < threshold and level in ['ERROR', 'FATAL']:
                entry.is_anomaly = True
                entry.anomaly_score = 1.0 - level_frequency
                anomalies.append({
                    'entry_id': entry.id,
                    'line_number': entry.line_number,
                    'level': level,
                    'message': entry.message,
                    'anomaly_score': entry.anomaly_score
                })
        
        self.db.commit()
        return anomalies

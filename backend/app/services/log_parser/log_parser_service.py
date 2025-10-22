from sqlalchemy.orm import Session
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
    def __init__(self, db: Session):
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
        log_file = self.db.query(LogFile).filter(LogFile.id == log_file_id).first()
        if not log_file:
            logger.error(f"Log file {log_file_id} not found")
            return
        
        try:
            # Update status to processing
            log_file.upload_status = "processing"
            self.db.commit()
            
            # Read and parse log file
            with open(log_file.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            log_entries = []
            for line_num, line in enumerate(lines, 1):
                parsed_entry = self.parse_log_line(line.strip(), line_num, log_file_id)
                if parsed_entry:
                    log_entries.append(parsed_entry)
            
            # Batch insert log entries
            if log_entries:
                self.db.bulk_insert_mappings(LogEntry, log_entries)
                self.db.commit()
                
                # Add to RAG system
                db_entries = self.db.query(LogEntry).filter(
                    LogEntry.log_file_id == log_file_id
                ).all()
                await self.rag_service.add_log_entries(db_entries)
            
            # Update log file status
            log_file.upload_status = "completed"
            log_file.is_processed = True
            self.db.commit()
            
            logger.info(f"Processed {len(log_entries)} log entries from {log_file.filename}")
            
        except Exception as e:
            logger.error(f"Error processing log file {log_file_id}: {str(e)}")
            log_file.upload_status = "failed"
            log_file.processing_error = str(e)
            self.db.commit()

    def parse_log_line(self, line: str, line_number: int, log_file_id: int) -> Optional[Dict[str, Any]]:
        """Parse a single log line and extract structured data"""
        if not line.strip():
            return None
        
        parsed_data = {
            'log_file_id': log_file_id,
            'line_number': line_number,
            'message': line,
            'raw_data': line,
            'parsed_data': {}
        }
        
        # Extract timestamp
        timestamp = self.extract_timestamp(line)
        if timestamp:
            parsed_data['timestamp'] = timestamp
            parsed_data['parsed_data']['timestamp'] = timestamp.isoformat()
        
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
        
        # Convert parsed_data to JSON string
        parsed_data['parsed_data'] = json.dumps(parsed_data['parsed_data'])
        
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
                return match.group(1) if match.groups() else match.group(0)
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

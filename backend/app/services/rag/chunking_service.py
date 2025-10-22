"""
Chunking Service for Loglytics AI
Smart text chunking for logs with semantic boundaries
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ChunkMetadata:
    """Metadata for a text chunk"""
    log_file_id: str
    project_id: str
    user_id: str
    chunk_index: int
    start_line: int
    end_line: int
    timestamp: Optional[datetime] = None
    log_level: Optional[str] = None
    source: Optional[str] = None
    file_type: Optional[str] = None

class ChunkingService:
    """Service for smart text chunking of log files"""
    
    def __init__(self):
        self.default_chunk_size = 800
        self.min_chunk_size = 500
        self.max_chunk_size = 1000
        self.overlap_size = 100
        self.preserve_boundaries = True
        
        # Log patterns for different formats
        self.log_patterns = {
            'standard': re.compile(r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\w+)\s+(.+)$'),
            'apache': re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)'),
            'nginx': re.compile(r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)\s+"([^"]+)"\s+"([^"]+)"'),
            'json': re.compile(r'^\{.*\}$'),
            'syslog': re.compile(r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(.+)$')
        }
    
    def chunk_log_file(
        self, 
        content: str, 
        metadata: ChunkMetadata,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk a log file into semantic chunks
        
        Args:
            content: Log file content
            metadata: Chunk metadata
            file_type: Type of log file (json, standard, apache, etc.)
            
        Returns:
            List of chunk dictionaries
        """
        try:
            lines = content.split('\n')
            if not lines:
                return []
            
            # Detect log format
            detected_type = file_type or self._detect_log_format(lines)
            
            # Parse log entries
            log_entries = self._parse_log_entries(lines, detected_type)
            
            # Create chunks
            chunks = self._create_chunks(log_entries, metadata, detected_type)
            
            logger.info(f"Created {len(chunks)} chunks from {len(lines)} lines")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking log file: {e}")
            return []
    
    def _detect_log_format(self, lines: List[str]) -> str:
        """
        Detect log format from sample lines
        
        Args:
            lines: Sample lines from log file
            
        Returns:
            Detected format type
        """
        # Check first 10 lines for format patterns
        sample_lines = lines[:10]
        
        for format_name, pattern in self.log_patterns.items():
            matches = sum(1 for line in sample_lines if pattern.match(line.strip()))
            if matches >= len(sample_lines) * 0.7:  # 70% match threshold
                return format_name
        
        # Default to standard format
        return 'standard'
    
    def _parse_log_entries(self, lines: List[str], format_type: str) -> List[Dict[str, Any]]:
        """
        Parse log lines into structured entries
        
        Args:
            lines: Log lines
            format_type: Detected format type
            
        Returns:
            List of parsed log entries
        """
        entries = []
        
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            entry = self._parse_log_line(line, format_type, i)
            if entry:
                entries.append(entry)
        
        return entries
    
    def _parse_log_line(self, line: str, format_type: str, line_number: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single log line
        
        Args:
            line: Log line
            format_type: Format type
            line_number: Line number
            
        Returns:
            Parsed entry or None
        """
        try:
            line = line.strip()
            
            if format_type == 'json':
                return self._parse_json_log(line, line_number)
            elif format_type == 'standard':
                return self._parse_standard_log(line, line_number)
            elif format_type == 'apache':
                return self._parse_apache_log(line, line_number)
            elif format_type == 'nginx':
                return self._parse_nginx_log(line, line_number)
            elif format_type == 'syslog':
                return self._parse_syslog_log(line, line_number)
            else:
                return self._parse_generic_log(line, line_number)
                
        except Exception as e:
            logger.debug(f"Error parsing log line {line_number}: {e}")
            return None
    
    def _parse_json_log(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parse JSON log entry"""
        try:
            data = json.loads(line)
            return {
                'line_number': line_number,
                'content': line,
                'timestamp': data.get('timestamp', data.get('time', data.get('@timestamp'))),
                'level': data.get('level', data.get('severity', data.get('log_level'))),
                'message': data.get('message', data.get('msg', str(data))),
                'source': data.get('source', data.get('service', data.get('logger'))),
                'metadata': data
            }
        except json.JSONDecodeError:
            return None
    
    def _parse_standard_log(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parse standard log entry"""
        match = self.log_patterns['standard'].match(line)
        if match:
            timestamp, level, message = match.groups()
            return {
                'line_number': line_number,
                'content': line,
                'timestamp': timestamp,
                'level': level,
                'message': message,
                'source': None,
                'metadata': {}
            }
        return None
    
    def _parse_apache_log(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parse Apache log entry"""
        match = self.log_patterns['apache'].match(line)
        if match:
            ip, timestamp, request, status, size = match.groups()
            return {
                'line_number': line_number,
                'content': line,
                'timestamp': timestamp,
                'level': 'INFO',
                'message': f"{request} - {status}",
                'source': 'apache',
                'metadata': {
                    'ip': ip,
                    'status': status,
                    'size': size
                }
            }
        return None
    
    def _parse_nginx_log(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parse Nginx log entry"""
        match = self.log_patterns['nginx'].match(line)
        if match:
            ip, timestamp, request, status, size, referer, user_agent = match.groups()
            return {
                'line_number': line_number,
                'content': line,
                'timestamp': timestamp,
                'level': 'INFO',
                'message': f"{request} - {status}",
                'source': 'nginx',
                'metadata': {
                    'ip': ip,
                    'status': status,
                    'size': size,
                    'referer': referer,
                    'user_agent': user_agent
                }
            }
        return None
    
    def _parse_syslog_log(self, line: str, line_number: int) -> Optional[Dict[str, Any]]:
        """Parse syslog entry"""
        match = self.log_patterns['syslog'].match(line)
        if match:
            timestamp, hostname, message = match.groups()
            return {
                'line_number': line_number,
                'content': line,
                'timestamp': timestamp,
                'level': 'INFO',
                'message': message,
                'source': hostname,
                'metadata': {}
            }
        return None
    
    def _parse_generic_log(self, line: str, line_number: int) -> Dict[str, Any]:
        """Parse generic log entry"""
        return {
            'line_number': line_number,
            'content': line,
            'timestamp': None,
            'level': None,
            'message': line,
            'source': None,
            'metadata': {}
        }
    
    def _create_chunks(
        self, 
        entries: List[Dict[str, Any]], 
        metadata: ChunkMetadata,
        format_type: str
    ) -> List[Dict[str, Any]]:
        """
        Create chunks from parsed log entries
        
        Args:
            entries: Parsed log entries
            metadata: Chunk metadata
            format_type: Log format type
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        if not entries:
            return chunks
        
        # Group entries by logical boundaries
        if format_type == 'json':
            chunks = self._create_json_chunks(entries, metadata)
        else:
            chunks = self._create_standard_chunks(entries, metadata)
        
        return chunks
    
    def _create_standard_chunks(
        self, 
        entries: List[Dict[str, Any]], 
        metadata: ChunkMetadata
    ) -> List[Dict[str, Any]]:
        """Create chunks for standard log formats"""
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for entry in entries:
            entry_size = len(entry['content'])
            
            # If adding this entry would exceed max size, finalize current chunk
            if current_size + entry_size > self.max_chunk_size and current_chunk:
                chunk = self._finalize_chunk(current_chunk, metadata, chunk_index)
                chunks.append(chunk)
                
                # Start new chunk with overlap
                current_chunk = self._create_overlap(current_chunk)
                current_size = sum(len(e['content']) for e in current_chunk)
                chunk_index += 1
            
            # Add entry to current chunk
            current_chunk.append(entry)
            current_size += entry_size
            
            # If chunk is large enough, consider finalizing it
            if current_size >= self.min_chunk_size and len(current_chunk) > 1:
                # Check if next entry would make it too large
                next_entry_size = 0
                if len(entries) > entries.index(entry) + 1:
                    next_entry = entries[entries.index(entry) + 1]
                    next_entry_size = len(next_entry['content'])
                
                if current_size + next_entry_size > self.max_chunk_size:
                    chunk = self._finalize_chunk(current_chunk, metadata, chunk_index)
                    chunks.append(chunk)
                    
                    # Start new chunk with overlap
                    current_chunk = self._create_overlap(current_chunk)
                    current_size = sum(len(e['content']) for e in current_chunk)
                    chunk_index += 1
        
        # Finalize last chunk
        if current_chunk:
            chunk = self._finalize_chunk(current_chunk, metadata, chunk_index)
            chunks.append(chunk)
        
        return chunks
    
    def _create_json_chunks(
        self, 
        entries: List[Dict[str, Any]], 
        metadata: ChunkMetadata
    ) -> List[Dict[str, Any]]:
        """Create chunks for JSON log format"""
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for entry in entries:
            entry_size = len(entry['content'])
            
            # For JSON logs, try to keep related entries together
            if current_size + entry_size > self.max_chunk_size and current_chunk:
                chunk = self._finalize_chunk(current_chunk, metadata, chunk_index)
                chunks.append(chunk)
                
                # Start new chunk with overlap
                current_chunk = self._create_overlap(current_chunk)
                current_size = sum(len(e['content']) for e in current_chunk)
                chunk_index += 1
            
            current_chunk.append(entry)
            current_size += entry_size
            
            # For JSON, we can be more flexible with chunk sizes
            if current_size >= self.min_chunk_size and len(current_chunk) > 1:
                # Check if we should finalize this chunk
                if current_size >= self.default_chunk_size:
                    chunk = self._finalize_chunk(current_chunk, metadata, chunk_index)
                    chunks.append(chunk)
                    
                    # Start new chunk with overlap
                    current_chunk = self._create_overlap(current_chunk)
                    current_size = sum(len(e['content']) for e in current_chunk)
                    chunk_index += 1
        
        # Finalize last chunk
        if current_chunk:
            chunk = self._finalize_chunk(current_chunk, metadata, chunk_index)
            chunks.append(chunk)
        
        return chunks
    
    def _finalize_chunk(
        self, 
        entries: List[Dict[str, Any]], 
        metadata: ChunkMetadata,
        chunk_index: int
    ) -> Dict[str, Any]:
        """Finalize a chunk with metadata"""
        if not entries:
            return {}
        
        # Create chunk content
        content = '\n'.join(entry['content'] for entry in entries)
        
        # Extract metadata from entries
        timestamps = [e['timestamp'] for e in entries if e['timestamp']]
        levels = [e['level'] for e in entries if e['level']]
        sources = [e['source'] for e in entries if e['source']]
        
        # Create chunk metadata
        chunk_metadata = ChunkMetadata(
            log_file_id=metadata.log_file_id,
            project_id=metadata.project_id,
            user_id=metadata.user_id,
            chunk_index=chunk_index,
            start_line=entries[0]['line_number'],
            end_line=entries[-1]['line_number'],
            timestamp=timestamps[0] if timestamps else None,
            log_level=levels[0] if levels else None,
            source=sources[0] if sources else None,
            file_type=metadata.file_type
        )
        
        return {
            'content': content,
            'metadata': chunk_metadata,
            'entry_count': len(entries),
            'size': len(content),
            'timestamps': timestamps,
            'levels': list(set(levels)),
            'sources': list(set(sources))
        }
    
    def _create_overlap(self, previous_chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create overlap from previous chunk"""
        if not previous_chunk:
            return []
        
        # Take last few entries for overlap
        overlap_entries = []
        overlap_size = 0
        
        for entry in reversed(previous_chunk):
            if overlap_size + len(entry['content']) <= self.overlap_size:
                overlap_entries.insert(0, entry)
                overlap_size += len(entry['content'])
            else:
                break
        
        return overlap_entries
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about chunks"""
        if not chunks:
            return {}
        
        sizes = [chunk['size'] for chunk in chunks]
        entry_counts = [chunk['entry_count'] for chunk in chunks]
        
        return {
            'total_chunks': len(chunks),
            'total_size': sum(sizes),
            'average_size': sum(sizes) / len(sizes),
            'min_size': min(sizes),
            'max_size': max(sizes),
            'total_entries': sum(entry_counts),
            'average_entries_per_chunk': sum(entry_counts) / len(chunks)
        }

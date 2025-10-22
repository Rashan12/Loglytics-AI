"""
Apache/Nginx Log Parser for Loglytics AI
Parses Apache and Nginx access and error logs
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class ApacheNginxParser:
    """Parser for Apache and Nginx log entries"""
    
    def __init__(self):
        # Apache Common Log Format
        self.apache_common_pattern = re.compile(
            r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)$'
        )
        
        # Apache Combined Log Format
        self.apache_combined_pattern = re.compile(
            r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)\s+"([^"]+)"\s+"([^"]+)"$'
        )
        
        # Apache Error Log Format
        self.apache_error_pattern = re.compile(
            r'^\[([^\]]+)\]\s+\[([^\]]+)\]\s+\[([^\]]+)\]\s+(.+)$'
        )
        
        # Nginx Access Log Format
        self.nginx_access_pattern = re.compile(
            r'^(\d+\.\d+\.\d+\.\d+)\s+-\s+-\s+\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+)\s+"([^"]+)"\s+"([^"]+)"\s+"([^"]+)"$'
        )
        
        # Nginx Error Log Format
        self.nginx_error_pattern = re.compile(
            r'^(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+\[([^\]]+)\]\s+(\d+)#(\d+):\s+(.+)$'
        )
        
        # Log level mapping
        self.log_levels = {
            "emerg": "EMERGENCY",
            "alert": "ALERT",
            "crit": "CRITICAL",
            "error": "ERROR",
            "warn": "WARNING",
            "notice": "NOTICE",
            "info": "INFO",
            "debug": "DEBUG"
        }
        
        # HTTP status code categories
        self.status_categories = {
            "1xx": "Informational",
            "2xx": "Success",
            "3xx": "Redirection",
            "4xx": "Client Error",
            "5xx": "Server Error"
        }
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse Apache/Nginx log content
        
        Args:
            content: Log content
            
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
                    entry = self._parse_log_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing log line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Log parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            logger.info(f"Parsed {len(parsed_entries)} Apache/Nginx log entries")
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing Apache/Nginx content: {e}")
            return []
    
    def _parse_log_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single log line"""
        try:
            # Try Apache access log formats
            match = self.apache_combined_pattern.match(line.strip())
            if match:
                return self._parse_apache_combined(match, line, line_num)
            
            match = self.apache_common_pattern.match(line.strip())
            if match:
                return self._parse_apache_common(match, line, line_num)
            
            # Try Apache error log format
            match = self.apache_error_pattern.match(line.strip())
            if match:
                return self._parse_apache_error(match, line, line_num)
            
            # Try Nginx access log format
            match = self.nginx_access_pattern.match(line.strip())
            if match:
                return self._parse_nginx_access(match, line, line_num)
            
            # Try Nginx error log format
            match = self.nginx_error_pattern.match(line.strip())
            if match:
                return self._parse_nginx_error(match, line, line_num)
            
            # Try to parse as generic web server log
            return self._parse_generic_web_log(line, line_num)
            
        except Exception as e:
            logger.debug(f"Error parsing log line {line_num}: {e}")
            return None
    
    def _parse_apache_combined(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Apache Combined Log Format"""
        try:
            ip, timestamp, request, status, size, referer, user_agent = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_apache_timestamp(timestamp)
            
            # Parse request
            request_info = self._parse_request(request)
            
            # Determine log level based on status code
            log_level = self._get_log_level_from_status(int(status))
            
            # Extract source
            source = "apache"
            
            # Extract service
            service = "web-server"
            
            # Extract metadata
            metadata = {
                "remote_ip": ip,
                "request": request,
                "status": int(status),
                "status_category": self._get_status_category(int(status)),
                "bytes": int(size),
                "referer": referer if referer != "-" else None,
                "user_agent": user_agent if user_agent != "-" else None,
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "protocol": request_info.get("protocol"),
                "format": "apache_combined"
            }
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": parsed_timestamp,
                "level": log_level,
                "message": f"{request_info.get('method', 'GET')} {request_info.get('path', '/')} - {status}",
                "source": source,
                "service": service,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.debug(f"Error parsing Apache combined format: {e}")
            return None
    
    def _parse_apache_common(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Apache Common Log Format"""
        try:
            ip, timestamp, request, status, size = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_apache_timestamp(timestamp)
            
            # Parse request
            request_info = self._parse_request(request)
            
            # Determine log level based on status code
            log_level = self._get_log_level_from_status(int(status))
            
            # Extract source
            source = "apache"
            
            # Extract service
            service = "web-server"
            
            # Extract metadata
            metadata = {
                "remote_ip": ip,
                "request": request,
                "status": int(status),
                "status_category": self._get_status_category(int(status)),
                "bytes": int(size),
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "protocol": request_info.get("protocol"),
                "format": "apache_common"
            }
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": parsed_timestamp,
                "level": log_level,
                "message": f"{request_info.get('method', 'GET')} {request_info.get('path', '/')} - {status}",
                "source": source,
                "service": service,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.debug(f"Error parsing Apache common format: {e}")
            return None
    
    def _parse_apache_error(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Apache Error Log Format"""
        try:
            timestamp, level, pid, message = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_apache_timestamp(timestamp)
            
            # Normalize log level
            log_level = self.log_levels.get(level.lower(), "ERROR")
            
            # Extract source
            source = "apache"
            
            # Extract service
            service = "web-server"
            
            # Extract metadata
            metadata = {
                "log_level": level,
                "pid": pid,
                "format": "apache_error"
            }
            
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
            logger.debug(f"Error parsing Apache error format: {e}")
            return None
    
    def _parse_nginx_access(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Nginx Access Log Format"""
        try:
            ip, timestamp, request, status, size, referer, user_agent, upstream = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_nginx_timestamp(timestamp)
            
            # Parse request
            request_info = self._parse_request(request)
            
            # Determine log level based on status code
            log_level = self._get_log_level_from_status(int(status))
            
            # Extract source
            source = "nginx"
            
            # Extract service
            service = "web-server"
            
            # Extract metadata
            metadata = {
                "remote_ip": ip,
                "request": request,
                "status": int(status),
                "status_category": self._get_status_category(int(status)),
                "bytes": int(size),
                "referer": referer if referer != "-" else None,
                "user_agent": user_agent if user_agent != "-" else None,
                "upstream": upstream if upstream != "-" else None,
                "method": request_info.get("method"),
                "path": request_info.get("path"),
                "protocol": request_info.get("protocol"),
                "format": "nginx_access"
            }
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": parsed_timestamp,
                "level": log_level,
                "message": f"{request_info.get('method', 'GET')} {request_info.get('path', '/')} - {status}",
                "source": source,
                "service": service,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.debug(f"Error parsing Nginx access format: {e}")
            return None
    
    def _parse_nginx_error(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse Nginx Error Log Format"""
        try:
            timestamp, level, pid, tid, message = match.groups()
            
            # Parse timestamp
            parsed_timestamp = self._parse_nginx_error_timestamp(timestamp)
            
            # Normalize log level
            log_level = self.log_levels.get(level.lower(), "ERROR")
            
            # Extract source
            source = "nginx"
            
            # Extract service
            service = "web-server"
            
            # Extract metadata
            metadata = {
                "log_level": level,
                "pid": int(pid),
                "tid": int(tid),
                "format": "nginx_error"
            }
            
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
            logger.debug(f"Error parsing Nginx error format: {e}")
            return None
    
    def _parse_generic_web_log(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse generic web server log line"""
        try:
            # Try to extract basic information
            timestamp = self._extract_timestamp_from_message(line)
            status = self._extract_status_from_message(line)
            ip = self._extract_ip_from_message(line)
            request = self._extract_request_from_message(line)
            
            # Determine log level
            log_level = self._get_log_level_from_status(status) if status else "INFO"
            
            # Extract source
            source = "web-server"
            
            # Extract service
            service = "web-server"
            
            # Extract metadata
            metadata = {
                "remote_ip": ip,
                "request": request,
                "status": status,
                "status_category": self._get_status_category(status) if status else None,
                "format": "generic_web"
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
            logger.debug(f"Error parsing generic web log: {e}")
            return None
    
    def _parse_apache_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse Apache timestamp format"""
        try:
            # Apache format: 25/Dec/2023:10:30:45 +0000
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            
            # Remove brackets
            timestamp = timestamp.strip('[]')
            
            # Parse format: 25/Dec/2023:10:30:45 +0000
            parts = timestamp.split(':')
            if len(parts) >= 4:
                date_part = parts[0]
                time_part = ':'.join(parts[1:4])
                tz_part = parts[4] if len(parts) > 4 else '+0000'
                
                # Parse date
                date_parts = date_part.split('/')
                if len(date_parts) >= 3:
                    day, month, year = date_parts[0], date_parts[1], date_parts[2]
                    month_num = month_map.get(month, '01')
                    
                    # Parse time
                    time_parts = time_part.split(':')
                    if len(time_parts) >= 3:
                        hour, minute, second = time_parts[0], time_parts[1], time_parts[2]
                        iso_timestamp = f"{year}-{month_num}-{day.zfill(2)}T{hour}:{minute}:{second}{tz_part}"
                        return iso_timestamp
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing Apache timestamp: {e}")
            return None
    
    def _parse_nginx_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse Nginx timestamp format"""
        try:
            # Nginx format: 25/Dec/2023:10:30:45 +0000
            return self._parse_apache_timestamp(timestamp)
            
        except Exception as e:
            logger.debug(f"Error parsing Nginx timestamp: {e}")
            return None
    
    def _parse_nginx_error_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse Nginx error timestamp format"""
        try:
            # Nginx error format: 2023/12/25 10:30:45
            try:
                parsed = datetime.strptime(timestamp, "%Y/%m/%d %H:%M:%S")
                return parsed.isoformat() + "Z"
            except ValueError:
                pass
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing Nginx error timestamp: {e}")
            return None
    
    def _parse_request(self, request: str) -> Dict[str, Any]:
        """Parse HTTP request"""
        try:
            # Format: "GET /path HTTP/1.1"
            parts = request.split()
            if len(parts) >= 3:
                method, path, protocol = parts[0], parts[1], parts[2]
                return {
                    "method": method,
                    "path": path,
                    "protocol": protocol
                }
            elif len(parts) >= 2:
                method, path = parts[0], parts[1]
                return {
                    "method": method,
                    "path": path,
                    "protocol": None
                }
            elif len(parts) >= 1:
                return {
                    "method": parts[0],
                    "path": None,
                    "protocol": None
                }
            
            return {}
            
        except Exception as e:
            logger.debug(f"Error parsing request: {e}")
            return {}
    
    def _get_log_level_from_status(self, status: int) -> str:
        """Get log level from HTTP status code"""
        try:
            if 200 <= status < 300:
                return "INFO"
            elif 300 <= status < 400:
                return "INFO"
            elif 400 <= status < 500:
                return "WARNING"
            elif 500 <= status < 600:
                return "ERROR"
            else:
                return "INFO"
                
        except Exception as e:
            logger.debug(f"Error getting log level from status: {e}")
            return "INFO"
    
    def _get_status_category(self, status: int) -> str:
        """Get status category from HTTP status code"""
        try:
            if 100 <= status < 200:
                return "1xx"
            elif 200 <= status < 300:
                return "2xx"
            elif 300 <= status < 400:
                return "3xx"
            elif 400 <= status < 500:
                return "4xx"
            elif 500 <= status < 600:
                return "5xx"
            else:
                return "unknown"
                
        except Exception as e:
            logger.debug(f"Error getting status category: {e}")
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
                    try:
                        parsed = date_parser.parse(timestamp_str)
                        return parsed.isoformat() + "Z"
                    except (ValueError, TypeError):
                        continue
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting timestamp from message: {e}")
            return None
    
    def _extract_status_from_message(self, message: str) -> Optional[int]:
        """Extract HTTP status code from message content"""
        try:
            # Look for status codes
            patterns = [
                r'\s(\d{3})\s',  # space status space
                r'"\s+(\d{3})\s+',  # quote space status space
                r'HTTP/\d\.\d"\s+(\d{3})',  # HTTP/1.1" status
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    status = int(match.group(1))
                    if 100 <= status <= 599:
                        return status
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting status from message: {e}")
            return None
    
    def _extract_ip_from_message(self, message: str) -> Optional[str]:
        """Extract IP address from message content"""
        try:
            # IP address pattern
            ip_pattern = r'(\d+\.\d+\.\d+\.\d+)'
            match = re.search(ip_pattern, message)
            if match:
                return match.group(1)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting IP from message: {e}")
            return None
    
    def _extract_request_from_message(self, message: str) -> Optional[str]:
        """Extract HTTP request from message content"""
        try:
            # Request pattern
            request_pattern = r'"([^"]+)"'
            match = re.search(request_pattern, message)
            if match:
                return match.group(1)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting request from message: {e}")
            return None
    
    def parse_batch(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse a batch of log lines"""
        try:
            parsed_entries = []
            
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = self._parse_log_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing log line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Log parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing log batch: {e}")
            return []

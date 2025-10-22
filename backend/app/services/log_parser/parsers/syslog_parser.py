"""
Syslog Parser for Loglytics AI
Parses syslog formatted log entries (RFC 5424)
"""

import re
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger(__name__)

class SyslogParser:
    """Parser for syslog formatted log entries"""
    
    def __init__(self):
        # RFC 5424 syslog format
        self.syslog_pattern = re.compile(
            r'^<(\d+)>(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.+)$'
        )
        
        # Legacy syslog format
        self.legacy_pattern = re.compile(
            r'^<(\d+)>(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(.+)$'
        )
        
        # Priority level mapping
        self.priority_levels = {
            0: "EMERGENCY",
            1: "ALERT", 
            2: "CRITICAL",
            3: "ERROR",
            4: "WARNING",
            5: "NOTICE",
            6: "INFO",
            7: "DEBUG"
        }
        
        # Facility mapping
        self.facilities = {
            0: "kernel",
            1: "user",
            2: "mail",
            3: "daemon",
            4: "auth",
            5: "syslog",
            6: "lpr",
            7: "news",
            8: "uucp",
            9: "cron",
            10: "authpriv",
            11: "ftp",
            12: "ntp",
            13: "security",
            14: "console",
            15: "solaris-cron",
            16: "local0",
            17: "local1",
            18: "local2",
            19: "local3",
            20: "local4",
            21: "local5",
            22: "local6",
            23: "local7"
        }
    
    def parse(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse syslog content
        
        Args:
            content: Syslog content
            
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
                    entry = self._parse_syslog_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing syslog line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Syslog parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            logger.info(f"Parsed {len(parsed_entries)} syslog entries")
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing syslog content: {e}")
            return []
    
    def _parse_syslog_line(self, line: str, line_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single syslog line"""
        try:
            # Try RFC 5424 format first
            match = self.syslog_pattern.match(line.strip())
            if match:
                return self._parse_rfc5424_format(match, line, line_num)
            
            # Try legacy format
            match = self.legacy_pattern.match(line.strip())
            if match:
                return self._parse_legacy_format(match, line, line_num)
            
            # Try to parse as generic syslog
            return self._parse_generic_syslog(line, line_num)
            
        except Exception as e:
            logger.debug(f"Error parsing syslog line {line_num}: {e}")
            return None
    
    def _parse_rfc5424_format(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse RFC 5424 syslog format"""
        try:
            priority, timestamp, hostname, app_name, proc_id, msg_id, message = match.groups()
            
            # Parse priority
            priority_int = int(priority)
            facility = priority_int // 8
            severity = priority_int % 8
            
            # Parse timestamp
            parsed_timestamp = self._parse_timestamp(timestamp)
            
            # Extract log level
            log_level = self.priority_levels.get(severity, "INFO")
            
            # Extract source
            source = app_name if app_name != "-" else None
            
            # Extract service
            service = hostname if hostname != "-" else None
            
            # Extract metadata
            metadata = {
                "facility": self.facilities.get(facility, f"facility_{facility}"),
                "severity": severity,
                "priority": priority_int,
                "hostname": hostname if hostname != "-" else None,
                "app_name": app_name if app_name != "-" else None,
                "proc_id": proc_id if proc_id != "-" else None,
                "msg_id": msg_id if msg_id != "-" else None
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
            logger.debug(f"Error parsing RFC 5424 format: {e}")
            return None
    
    def _parse_legacy_format(self, match: re.Match, line: str, line_num: int) -> Dict[str, Any]:
        """Parse legacy syslog format"""
        try:
            priority, timestamp, hostname, message = match.groups()
            
            # Parse priority
            priority_int = int(priority)
            facility = priority_int // 8
            severity = priority_int % 8
            
            # Parse timestamp (legacy format)
            parsed_timestamp = self._parse_legacy_timestamp(timestamp)
            
            # Extract log level
            log_level = self.priority_levels.get(severity, "INFO")
            
            # Extract source
            source = None
            
            # Extract service
            service = hostname
            
            # Extract metadata
            metadata = {
                "facility": self.facilities.get(facility, f"facility_{facility}"),
                "severity": severity,
                "priority": priority_int,
                "hostname": hostname,
                "format": "legacy"
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
            logger.debug(f"Error parsing legacy format: {e}")
            return None
    
    def _parse_generic_syslog(self, line: str, line_num: int) -> Dict[str, Any]:
        """Parse generic syslog line"""
        try:
            # Try to extract priority
            priority_match = re.match(r'^<(\d+)>', line)
            if priority_match:
                priority = int(priority_match.group(1))
                facility = priority // 8
                severity = priority % 8
                log_level = self.priority_levels.get(severity, "INFO")
                
                # Remove priority from line
                message = line[priority_match.end():].strip()
            else:
                log_level = "INFO"
                message = line
                facility = 0
                severity = 6
            
            # Try to extract timestamp
            timestamp = self._extract_timestamp_from_message(message)
            
            # Try to extract hostname
            hostname = self._extract_hostname_from_message(message)
            
            # Extract metadata
            metadata = {
                "facility": self.facilities.get(facility, f"facility_{facility}"),
                "severity": severity,
                "priority": priority if priority_match else None,
                "hostname": hostname,
                "format": "generic"
            }
            
            return {
                "line_number": line_num,
                "content": line,
                "timestamp": timestamp,
                "level": log_level,
                "message": message,
                "source": None,
                "service": hostname,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.debug(f"Error parsing generic syslog: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse RFC 5424 timestamp"""
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
                "%Y-%m-%dT%H:%M:%S%z"
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
    
    def _parse_legacy_timestamp(self, timestamp: str) -> Optional[str]:
        """Parse legacy syslog timestamp"""
        try:
            # Legacy format: Dec 25 10:30:45
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            
            parts = timestamp.split()
            if len(parts) >= 3:
                month, day, time = parts[0], parts[1], parts[2]
                month_num = month_map.get(month, '01')
                current_year = datetime.now().year
                
                # Parse time
                time_parts = time.split(':')
                if len(time_parts) >= 3:
                    hour, minute, second = time_parts[0], time_parts[1], time_parts[2]
                    iso_timestamp = f"{current_year}-{month_num}-{day.zfill(2)}T{hour}:{minute}:{second}Z"
                    return iso_timestamp
            
            return None
            
        except Exception as e:
            logger.debug(f"Error parsing legacy timestamp: {e}")
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
    
    def _extract_hostname_from_message(self, message: str) -> Optional[str]:
        """Extract hostname from message content"""
        try:
            # Common hostname patterns
            patterns = [
                r'^(\S+):',  # hostname: at start
                r'(\S+)\s+',  # hostname at start
                r'\[(\S+)\]',  # [hostname]
            ]
            
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    hostname = match.group(1)
                    # Validate hostname format
                    if re.match(r'^[a-zA-Z0-9.-]+$', hostname):
                        return hostname
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extracting hostname from message: {e}")
            return None
    
    def parse_batch(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse a batch of syslog lines"""
        try:
            parsed_entries = []
            
            for line_num, line in enumerate(lines, 1):
                if not line.strip():
                    continue
                
                try:
                    entry = self._parse_syslog_line(line, line_num)
                    if entry:
                        parsed_entries.append(entry)
                except Exception as e:
                    logger.warning(f"Error parsing syslog line {line_num}: {e}")
                    # Create error entry
                    parsed_entries.append({
                        "line_number": line_num,
                        "content": line,
                        "error": str(e),
                        "timestamp": None,
                        "level": "ERROR",
                        "message": f"Syslog parsing error: {str(e)}",
                        "source": None,
                        "metadata": {"parse_error": True}
                    })
            
            return parsed_entries
            
        except Exception as e:
            logger.error(f"Error parsing syslog batch: {e}")
            return []
    
    def get_priority_info(self, priority: int) -> Dict[str, Any]:
        """Get priority information"""
        try:
            facility = priority // 8
            severity = priority % 8
            
            return {
                "priority": priority,
                "facility": facility,
                "facility_name": self.facilities.get(facility, f"facility_{facility}"),
                "severity": severity,
                "severity_name": self.priority_levels.get(severity, "INFO")
            }
            
        except Exception as e:
            logger.debug(f"Error getting priority info: {e}")
            return {}
    
    def validate_syslog_format(self, line: str) -> bool:
        """Validate syslog format"""
        try:
            # Check for priority
            if not re.match(r'^<\d+>', line):
                return False
            
            # Try to match known patterns
            if self.syslog_pattern.match(line) or self.legacy_pattern.match(line):
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error validating syslog format: {e}")
            return False

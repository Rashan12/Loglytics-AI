"""
DoS Protection and Security Scanning
Provides protection against denial of service attacks and security scanning
"""

import asyncio
import time
import hashlib
import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class DoSProtection:
    """Denial of Service protection system"""
    
    def __init__(self):
        self.connection_limits = {
            "per_ip": 10,  # Max connections per IP
            "per_user": 5,  # Max connections per user
            "global": 1000  # Global connection limit
        }
        
        self.request_limits = {
            "per_ip_per_minute": 60,
            "per_user_per_minute": 30,
            "per_ip_per_hour": 1000,
            "per_user_per_hour": 500
        }
        
        self.size_limits = {
            "max_request_size": 10 * 1024 * 1024,  # 10MB
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "max_json_size": 1024 * 1024,  # 1MB
        }
        
        self.timeout_limits = {
            "request_timeout": 300,  # 5 minutes
            "websocket_timeout": 3600,  # 1 hour
            "celery_task_timeout": 1800,  # 30 minutes
        }
        
        # Tracking structures
        self.connections: Dict[str, Set[str]] = defaultdict(set)  # IP -> connection_ids
        self.user_connections: Dict[str, Set[str]] = defaultdict(set)  # user_id -> connection_ids
        self.request_counts: Dict[str, deque] = defaultdict(deque)  # IP -> timestamps
        self.user_request_counts: Dict[str, deque] = defaultdict(deque)  # user_id -> timestamps
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Dict[str, int] = defaultdict(int)
        
        # Cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background cleanup task"""
        # Only schedule background task when an event loop is running.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop (e.g., during import/pytest collection); defer startup.
            self._cleanup_task = None
            return
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = loop.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background cleanup loop"""
        while True:
            try:
                await self._cleanup_expired_data()
                await asyncio.sleep(60)  # Cleanup every minute
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_data(self):
        """Clean up expired tracking data"""
        now = time.time()
        cutoff_minute = now - 60
        cutoff_hour = now - 3600
        
        # Clean up request counts
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = deque(
                [t for t in self.request_counts[ip] if t > cutoff_hour]
            )
            if not self.request_counts[ip]:
                del self.request_counts[ip]
        
        for user_id in list(self.user_request_counts.keys()):
            self.user_request_counts[user_id] = deque(
                [t for t in self.user_request_counts[user_id] if t > cutoff_hour]
            )
            if not self.user_request_counts[user_id]:
                del self.user_request_counts[user_id]
    
    def check_connection_limit(self, ip: str, connection_id: str) -> Tuple[bool, str]:
        """Check if IP has exceeded connection limit"""
        try:
            # Check per-IP limit
            if len(self.connections[ip]) >= self.connection_limits["per_ip"]:
                return False, f"IP {ip} has exceeded connection limit"
            
            # Check global limit
            total_connections = sum(len(conns) for conns in self.connections.values())
            if total_connections >= self.connection_limits["global"]:
                return False, "Global connection limit exceeded"
            
            # Add connection
            self.connections[ip].add(connection_id)
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking connection limit: {e}")
            return False, "Connection limit check failed"
    
    def check_user_connection_limit(self, user_id: str, connection_id: str) -> Tuple[bool, str]:
        """Check if user has exceeded connection limit"""
        try:
            if len(self.user_connections[user_id]) >= self.connection_limits["per_user"]:
                return False, f"User {user_id} has exceeded connection limit"
            
            # Add connection
            self.user_connections[user_id].add(connection_id)
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking user connection limit: {e}")
            return False, "User connection limit check failed"
    
    def check_request_rate_limit(self, ip: str) -> Tuple[bool, str]:
        """Check if IP has exceeded request rate limit"""
        try:
            now = time.time()
            
            # Add current request
            self.request_counts[ip].append(now)
            
            # Check per-minute limit
            minute_cutoff = now - 60
            recent_requests = [t for t in self.request_counts[ip] if t > minute_cutoff]
            
            if len(recent_requests) > self.request_limits["per_ip_per_minute"]:
                self.suspicious_ips[ip] += 1
                if self.suspicious_ips[ip] > 10:
                    self.blocked_ips.add(ip)
                    logger.warning(f"IP {ip} blocked due to suspicious activity")
                return False, f"IP {ip} has exceeded request rate limit"
            
            # Check per-hour limit
            hour_cutoff = now - 3600
            hour_requests = [t for t in self.request_counts[ip] if t > hour_cutoff]
            
            if len(hour_requests) > self.request_limits["per_ip_per_hour"]:
                self.suspicious_ips[ip] += 1
                return False, f"IP {ip} has exceeded hourly request limit"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking request rate limit: {e}")
            return False, "Request rate limit check failed"
    
    def check_user_request_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """Check if user has exceeded request rate limit"""
        try:
            now = time.time()
            
            # Add current request
            self.user_request_counts[user_id].append(now)
            
            # Check per-minute limit
            minute_cutoff = now - 60
            recent_requests = [t for t in self.user_request_counts[user_id] if t > minute_cutoff]
            
            if len(recent_requests) > self.request_limits["per_user_per_minute"]:
                return False, f"User {user_id} has exceeded request rate limit"
            
            # Check per-hour limit
            hour_cutoff = now - 3600
            hour_requests = [t for t in self.user_request_counts[user_id] if t > hour_cutoff]
            
            if len(hour_requests) > self.request_limits["per_user_per_hour"]:
                return False, f"User {user_id} has exceeded hourly request limit"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error checking user request rate limit: {e}")
            return False, "User request rate limit check failed"
    
    def check_request_size(self, content_length: int) -> Tuple[bool, str]:
        """Check if request size exceeds limit"""
        if content_length > self.size_limits["max_request_size"]:
            return False, f"Request too large: {content_length} bytes"
        return True, ""
    
    def check_file_size(self, file_size: int) -> Tuple[bool, str]:
        """Check if file size exceeds limit"""
        if file_size > self.size_limits["max_file_size"]:
            return False, f"File too large: {file_size} bytes"
        return True, ""
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Block IP address"""
        self.blocked_ips.add(ip)
        logger.warning(f"IP {ip} blocked for {duration} seconds")
        
        # Schedule unblock
        asyncio.create_task(self._unblock_ip_after(ip, duration))
    
    async def _unblock_ip_after(self, ip: str, duration: int):
        """Unblock IP after duration"""
        await asyncio.sleep(duration)
        self.blocked_ips.discard(ip)
        logger.info(f"IP {ip} unblocked")
    
    def remove_connection(self, ip: str, connection_id: str):
        """Remove connection from tracking"""
        self.connections[ip].discard(connection_id)
        if not self.connections[ip]:
            del self.connections[ip]
    
    def remove_user_connection(self, user_id: str, connection_id: str):
        """Remove user connection from tracking"""
        self.user_connections[user_id].discard(connection_id)
        if not self.user_connections[user_id]:
            del self.user_connections[user_id]
    
    def get_stats(self) -> Dict[str, any]:
        """Get DoS protection statistics"""
        return {
            "total_connections": sum(len(conns) for conns in self.connections.values()),
            "total_users": len(self.user_connections),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "tracked_ips": len(self.request_counts),
            "tracked_users": len(self.user_request_counts)
        }


class SecurityScanner:
    """Security scanner for uploaded files and content"""
    
    def __init__(self):
        self.malicious_patterns = [
            # Script injection patterns
            r"<script[^>]*>.*</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"onfocus\s*=",
            r"onblur\s*=",
            r"onchange\s*=",
            r"onsubmit\s*=",
            r"onreset\s*=",
            r"onselect\s*=",
            r"onkeydown\s*=",
            r"onkeyup\s*=",
            r"onkeypress\s*=",
            
            # Code execution patterns
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\(",
            r"proc_open\s*\(",
            r"popen\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\(",
            r"proc_open\s*\(",
            r"popen\s*\(",
            
            # File inclusion patterns
            r"include\s*\(",
            r"require\s*\(",
            r"require_once\s*\(",
            r"include_once\s*\(",
            r"file_get_contents\s*\(",
            r"fopen\s*\(",
            r"fwrite\s*\(",
            r"fputs\s*\(",
            
            # SQL injection patterns
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"insert\s+into",
            r"update\s+set",
            r"alter\s+table",
            r"create\s+table",
            r"truncate\s+table",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_executesql",
            r"xp_cmdshell",
            r"';.*--",
            r"'.*or.*1=1",
            r"'.*and.*1=1",
            
            # Path traversal patterns
            r"\.\./",
            r"\.\.\\",
            r"%2e%2e%2f",
            r"%2e%2e%5c",
            r"\.\.%2f",
            r"\.\.%5c",
            
            # Command injection patterns
            r"\|",
            r"&",
            r";",
            r"`",
            r"\$",
            r"\(",
            r"\)",
            r"<",
            r">",
            r"\*",
            r"\?",
            r"\[",
            r"\]",
            r"\{",
            r"\}",
            r"!",
            r"#",
            r"@",
            r"%",
            r"^",
            r"~",
            r"`",
            
            # Suspicious file paths
            r"/etc/passwd",
            r"/etc/shadow",
            r"/etc/hosts",
            r"C:\\Windows\\System32",
            r"C:\\Windows\\SysWOW64",
            r"/bin/",
            r"/sbin/",
            r"/usr/bin/",
            r"/usr/sbin/",
            r"/var/log/",
            r"/tmp/",
            r"/var/tmp/",
            
            # Malware signatures (basic)
            r"malware",
            r"trojan",
            r"virus",
            r"backdoor",
            r"rootkit",
            r"keylogger",
            r"spyware",
            r"adware",
        ]
        
        self.quarantine_dir = "/tmp/quarantine"
        self.scan_results: Dict[str, Dict[str, any]] = {}
    
    def scan_content(self, content: str, filename: str = "") -> Tuple[bool, List[str], Dict[str, any]]:
        """
        Scan content for malicious patterns
        
        Args:
            content: Content to scan
            filename: Original filename
            
        Returns:
            Tuple of (is_safe, threats_found, scan_details)
        """
        try:
            threats_found = []
            scan_details = {
                "filename": filename,
                "content_length": len(content),
                "scan_timestamp": datetime.utcnow().isoformat(),
                "threats": [],
                "risk_level": "low"
            }
            
            # Convert to lowercase for case-insensitive matching
            content_lower = content.lower()
            
            # Check for malicious patterns
            for pattern in self.malicious_patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    threat_info = {
                        "pattern": pattern,
                        "matches": matches,
                        "severity": self._get_threat_severity(pattern)
                    }
                    threats_found.append(pattern)
                    scan_details["threats"].append(threat_info)
            
            # Determine risk level
            if threats_found:
                severities = [t["severity"] for t in scan_details["threats"]]
                if "high" in severities:
                    scan_details["risk_level"] = "high"
                elif "medium" in severities:
                    scan_details["risk_level"] = "medium"
                else:
                    scan_details["risk_level"] = "low"
            
            is_safe = len(threats_found) == 0
            scan_details["is_safe"] = is_safe
            
            # Store scan results
            scan_id = hashlib.md5(f"{filename}{content[:100]}".encode()).hexdigest()
            self.scan_results[scan_id] = scan_details
            
            return is_safe, threats_found, scan_details
            
        except Exception as e:
            logger.error(f"Error scanning content: {e}")
            return False, ["scan_error"], {"error": str(e)}
    
    def _get_threat_severity(self, pattern: str) -> str:
        """Get threat severity based on pattern"""
        high_severity_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\(",
            r"proc_open\s*\(",
            r"popen\s*\(",
            r"xp_cmdshell",
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"alter\s+table",
            r"truncate\s+table",
        ]
        
        medium_severity_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"include\s*\(",
            r"require\s*\(",
            r"file_get_contents\s*\(",
            r"fopen\s*\(",
            r"\.\./",
            r"\.\.\\",
        ]
        
        if any(re.search(p, pattern, re.IGNORECASE) for p in high_severity_patterns):
            return "high"
        elif any(re.search(p, pattern, re.IGNORECASE) for p in medium_severity_patterns):
            return "medium"
        else:
            return "low"
    
    async def quarantine_file(self, file_path: str, reason: str) -> bool:
        """Quarantine suspicious file"""
        try:
            import os
            import shutil
            
            # Create quarantine directory if it doesn't exist
            os.makedirs(self.quarantine_dir, exist_ok=True)
            
            # Generate quarantine filename
            filename = os.path.basename(file_path)
            quarantine_path = os.path.join(
                self.quarantine_dir,
                f"{int(time.time())}_{filename}"
            )
            
            # Move file to quarantine
            shutil.move(file_path, quarantine_path)
            
            # Log quarantine event
            logger.warning(f"File quarantined: {file_path} -> {quarantine_path} (reason: {reason})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error quarantining file: {e}")
            return False
    
    def get_scan_stats(self) -> Dict[str, any]:
        """Get security scan statistics"""
        total_scans = len(self.scan_results)
        unsafe_files = sum(1 for r in self.scan_results.values() if not r.get("is_safe", True))
        
        threat_counts = {"high": 0, "medium": 0, "low": 0}
        for result in self.scan_results.values():
            risk_level = result.get("risk_level", "low")
            threat_counts[risk_level] += 1
        
        return {
            "total_scans": total_scans,
            "unsafe_files": unsafe_files,
            "safe_files": total_scans - unsafe_files,
            "threat_counts": threat_counts,
            "quarantine_directory": self.quarantine_dir
        }


# Global instances
dos_protection = DoSProtection()
security_scanner = SecurityScanner()

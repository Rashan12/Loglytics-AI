"""
Input Validation and Sanitization
Comprehensive input validation for all user inputs
"""

import re
import magic
import hashlib
import mimetypes
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import logging
from urllib.parse import urlparse
import bleach
from PIL import Image
import io

logger = logging.getLogger(__name__)


class FileValidator:
    """File upload validation and scanning"""
    
    def __init__(self):
        self.allowed_extensions = {
            ".log", ".txt", ".json", ".csv", ".xml", ".yaml", ".yml",
            ".gz", ".zip", ".tar", ".tar.gz", ".bz2", ".xz"
        }
        self.allowed_mime_types = {
            "text/plain", "application/json", "text/csv", "application/xml",
            "text/yaml", "application/gzip", "application/zip", "application/x-tar",
            "application/x-bzip2", "application/x-xz"
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.malicious_patterns = [
            r"<script[^>]*>.*</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"eval\s*\(",
            r"exec\s*\(",
            r"system\s*\(",
            r"shell_exec\s*\(",
            r"passthru\s*\(",
            r"proc_open\s*\(",
            r"popen\s*\(",
            r"file_get_contents\s*\(",
            r"fopen\s*\(",
            r"fwrite\s*\(",
            r"fputs\s*\(",
            r"include\s*\(",
            r"require\s*\(",
            r"require_once\s*\(",
            r"include_once\s*\(",
        ]
    
    def validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate uploaded file
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message, file_info)
        """
        try:
            file_info = {
                "original_filename": filename,
                "size": len(file_content),
                "extension": Path(filename).suffix.lower(),
                "mime_type": None,
                "is_compressed": False,
                "is_text": False,
                "is_safe": True
            }
            
            # Check file size
            if file_info["size"] > self.max_file_size:
                return False, "File too large (max 100MB)", file_info
            
            # Check file extension
            if file_info["extension"] not in self.allowed_extensions:
                return False, f"File type not allowed: {file_info['extension']}", file_info
            
            # Detect MIME type
            try:
                mime_type = magic.from_buffer(file_content, mime=True)
                file_info["mime_type"] = mime_type
            except Exception:
                # Fallback to mimetypes
                mime_type, _ = mimetypes.guess_type(filename)
                file_info["mime_type"] = mime_type or "application/octet-stream"
            
            # Validate MIME type
            if mime_type not in self.allowed_mime_types:
                return False, f"MIME type not allowed: {mime_type}", file_info
            
            # Check for compressed files
            if mime_type in ["application/gzip", "application/zip", "application/x-tar"]:
                file_info["is_compressed"] = True
            
            # Check if it's a text file
            try:
                content_str = file_content.decode('utf-8')
                file_info["is_text"] = True
                
                # Scan for malicious content
                if self._scan_for_malicious_content(content_str):
                    file_info["is_safe"] = False
                    return False, "File contains potentially malicious content", file_info
                    
            except UnicodeDecodeError:
                # Binary file
                file_info["is_text"] = False
                
                # For binary files, check for executable signatures
                if self._is_executable_file(file_content):
                    return False, "Executable files are not allowed", file_info
            
            return True, "", file_info
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return False, "Error validating file", {}
    
    def _scan_for_malicious_content(self, content: str) -> bool:
        """Scan file content for malicious patterns"""
        try:
            content_lower = content.lower()
            
            for pattern in self.malicious_patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    logger.warning(f"Malicious pattern detected: {pattern}")
                    return True
            
            # Check for suspicious file paths
            suspicious_paths = [
                r"/etc/passwd",
                r"/etc/shadow",
                r"/etc/hosts",
                r"C:\\Windows\\System32",
                r"C:\\Windows\\SysWOW64",
                r"/bin/",
                r"/sbin/",
                r"/usr/bin/",
                r"/usr/sbin/",
            ]
            
            for path_pattern in suspicious_paths:
                if re.search(path_pattern, content_lower):
                    logger.warning(f"Suspicious path detected: {path_pattern}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error scanning content: {e}")
            return True  # Err on the side of caution
    
    def _is_executable_file(self, content: bytes) -> bool:
        """Check if file is executable"""
        try:
            # Check for common executable signatures
            executable_signatures = [
                b'\x4d\x5a',  # PE executable
                b'\x7f\x45\x4c\x46',  # ELF executable
                b'\xfe\xed\xfa',  # Mach-O executable
                b'\xce\xfa\xed\xfe',  # Mach-O executable (64-bit)
                b'\xca\xfe\xba\xbe',  # Mach-O fat binary
            ]
            
            for signature in executable_signatures:
                if content.startswith(signature):
                    return True
            
            # Check for shebang
            if content.startswith(b'#!'):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking executable: {e}")
            return True  # Err on the side of caution


class URLValidator:
    """URL validation and sanitization"""
    
    def __init__(self):
        self.allowed_schemes = {"http", "https"}
        self.blocked_domains = {
            "localhost", "127.0.0.1", "0.0.0.0", "::1",
            "example.com", "test.com", "invalid.com"
        }
        self.max_url_length = 2048
    
    def validate_url(self, url: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate URL
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message, url_info)
        """
        try:
            url_info = {
                "original_url": url,
                "scheme": None,
                "domain": None,
                "path": None,
                "is_safe": True
            }
            
            if not url:
                return False, "URL is required", url_info
            
            if len(url) > self.max_url_length:
                return False, "URL too long", url_info
            
            # Parse URL
            parsed = urlparse(url)
            url_info["scheme"] = parsed.scheme
            url_info["domain"] = parsed.netloc
            url_info["path"] = parsed.path
            
            # Check scheme
            if parsed.scheme not in self.allowed_schemes:
                return False, f"Scheme not allowed: {parsed.scheme}", url_info
            
            # Check domain
            if not parsed.netloc:
                return False, "Invalid domain", url_info
            
            # Check for blocked domains
            domain = parsed.netloc.lower()
            if domain in self.blocked_domains:
                return False, f"Domain not allowed: {domain}", url_info
            
            # Check for suspicious patterns
            if self._is_suspicious_url(url):
                url_info["is_safe"] = False
                return False, "Suspicious URL detected", url_info
            
            return True, "", url_info
            
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False, "Invalid URL format", {}
    
    def _is_suspicious_url(self, url: str) -> bool:
        """Check for suspicious URL patterns"""
        suspicious_patterns = [
            r"javascript:",
            r"vbscript:",
            r"data:",
            r"file:",
            r"ftp:",
            r"gopher:",
            r"mailto:",
            r"tel:",
            r"<script",
            r"</script>",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"expression\s*\(",
        ]
        
        url_lower = url.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, url_lower):
                return True
        
        return False


class SearchQueryValidator:
    """Search query validation and sanitization"""
    
    def __init__(self):
        self.max_query_length = 1000
        self.dangerous_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"insert\s+into",
            r"update\s+set",
            r"exec\s*\(",
            r"execute\s*\(",
            r"sp_executesql",
            r"xp_cmdshell",
            r"';.*--",
            r"'.*or.*1=1",
            r"'.*and.*1=1",
            r"<script",
            r"</script>",
            r"javascript:",
            r"vbscript:",
        ]
    
    def validate_search_query(self, query: str) -> Tuple[bool, str, str]:
        """
        Validate search query
        
        Args:
            query: Search query to validate
            
        Returns:
            Tuple of (is_valid, error_message, sanitized_query)
        """
        try:
            if not query:
                return True, "", ""
            
            if len(query) > self.max_query_length:
                return False, "Query too long", ""
            
            # Check for dangerous patterns
            query_lower = query.lower()
            for pattern in self.dangerous_patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return False, "Query contains potentially dangerous content", ""
            
            # Sanitize query
            sanitized = self._sanitize_query(query)
            
            return True, "", sanitized
            
        except Exception as e:
            logger.error(f"Error validating search query: {e}")
            return False, "Error validating query", ""
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize search query"""
        # Remove null bytes
        sanitized = query.replace("\x00", "")
        
        # Remove control characters
        sanitized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", sanitized)
        
        # Remove HTML tags
        sanitized = bleach.clean(sanitized, tags=[], strip=True)
        
        # Limit length
        sanitized = sanitized[:self.max_query_length]
        
        return sanitized.strip()


class EmailValidator:
    """Email validation and sanitization"""
    
    def __init__(self):
        self.email_pattern = re.compile(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        self.max_email_length = 254
        self.blocked_domains = {
            "tempmail.com", "10minutemail.com", "guerrillamail.com",
            "mailinator.com", "throwaway.email"
        }
    
    def validate_email(self, email: str) -> Tuple[bool, str, str]:
        """
        Validate email address
        
        Args:
            email: Email to validate
            
        Returns:
            Tuple of (is_valid, error_message, sanitized_email)
        """
        try:
            if not email:
                return False, "Email is required", ""
            
            if len(email) > self.max_email_length:
                return False, "Email too long", ""
            
            # Basic format validation
            if not self.email_pattern.match(email):
                return False, "Invalid email format", ""
            
            # Sanitize email
            sanitized = email.lower().strip()
            
            # Check domain
            domain = sanitized.split("@")[1]
            if domain in self.blocked_domains:
                return False, "Email domain not allowed", ""
            
            return True, "", sanitized
            
        except Exception as e:
            logger.error(f"Error validating email: {e}")
            return False, "Error validating email", ""


class JSONValidator:
    """JSON validation and sanitization"""
    
    def __init__(self):
        self.max_depth = 10
        self.max_keys = 1000
        self.max_string_length = 10000
    
    def validate_json(self, data: Any, max_depth: int = None) -> Tuple[bool, str, Any]:
        """
        Validate JSON data
        
        Args:
            data: JSON data to validate
            max_depth: Maximum nesting depth
            
        Returns:
            Tuple of (is_valid, error_message, sanitized_data)
        """
        try:
            max_depth = max_depth or self.max_depth
            
            # Check depth
            if self._get_depth(data) > max_depth:
                return False, "JSON too deeply nested", None
            
            # Check number of keys
            if self._count_keys(data) > self.max_keys:
                return False, "Too many keys in JSON", None
            
            # Sanitize data
            sanitized = self._sanitize_json_data(data)
            
            return True, "", sanitized
            
        except Exception as e:
            logger.error(f"Error validating JSON: {e}")
            return False, "Error validating JSON", None
    
    def _get_depth(self, data: Any, current_depth: int = 0) -> int:
        """Get maximum depth of nested data"""
        if isinstance(data, dict):
            if not data:
                return current_depth
            return max(self._get_depth(value, current_depth + 1) for value in data.values())
        elif isinstance(data, list):
            if not data:
                return current_depth
            return max(self._get_depth(item, current_depth + 1) for item in data)
        else:
            return current_depth
    
    def _count_keys(self, data: Any) -> int:
        """Count total number of keys in nested data"""
        if isinstance(data, dict):
            return len(data) + sum(self._count_keys(value) for value in data.values())
        elif isinstance(data, list):
            return sum(self._count_keys(item) for item in data)
        else:
            return 0
    
    def _sanitize_json_data(self, data: Any) -> Any:
        """Sanitize JSON data recursively"""
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Sanitize key
                clean_key = str(key)[:100]  # Limit key length
                clean_key = re.sub(r'[^\w\-_.]', '_', clean_key)
                
                # Sanitize value
                clean_value = self._sanitize_json_data(value)
                sanitized[clean_key] = clean_value
            
            return sanitized
        
        elif isinstance(data, list):
            return [self._sanitize_json_data(item) for item in data]
        
        elif isinstance(data, str):
            # Sanitize string
            sanitized = data[:self.max_string_length]  # Limit length
            sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)  # Remove control chars
            return sanitized
        
        else:
            return data


class InputValidator:
    """Main input validator that coordinates all validators"""
    
    def __init__(self):
        self.file_validator = FileValidator()
        self.url_validator = URLValidator()
        self.search_validator = SearchQueryValidator()
        self.email_validator = EmailValidator()
        self.json_validator = JSONValidator()
    
    def validate_file_upload(self, file_content: bytes, filename: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate file upload"""
        return self.file_validator.validate_file(file_content, filename)
    
    def validate_url(self, url: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Validate URL"""
        return self.url_validator.validate_url(url)
    
    def validate_search_query(self, query: str) -> Tuple[bool, str, str]:
        """Validate search query"""
        return self.search_validator.validate_search_query(query)
    
    def validate_email(self, email: str) -> Tuple[bool, str, str]:
        """Validate email"""
        return self.email_validator.validate_email(email)
    
    def validate_json(self, data: Any) -> Tuple[bool, str, Any]:
        """Validate JSON data"""
        return self.json_validator.validate_json(data)
    
    def sanitize_string(self, input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not input_str:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', input_str)
        
        # Remove HTML tags
        sanitized = bleach.clean(sanitized, tags=[], strip=True)
        
        # Limit length
        sanitized = sanitized[:max_length]
        
        return sanitized.strip()
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename"""
        if not filename:
            return "unnamed"
        
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading dots and spaces
        filename = filename.lstrip('. ')
        
        # Limit length
        filename = filename[:255]
        
        return filename or "unnamed"


# Global validator instance
input_validator = InputValidator()

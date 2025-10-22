from typing import Any, Dict, List, Optional
import json
import re
from datetime import datetime
import hashlib
import redis
from app.config import settings


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely load JSON string, return default if fails"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(data: Any) -> str:
    """Safely dump data to JSON string"""
    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return "{}"


def extract_emails(text: str) -> List[str]:
    """Extract email addresses from text"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, text)


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)


def extract_ip_addresses(text: str) -> List[str]:
    """Extract IP addresses from text"""
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    return re.findall(ip_pattern, text)


def generate_hash(text: str) -> str:
    """Generate MD5 hash of text"""
    return hashlib.md5(text.encode()).hexdigest()


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    elif seconds < 86400:
        return f"{seconds/3600:.1f}h"
    else:
        return f"{seconds/86400:.1f}d"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def clean_filename(filename: str) -> str:
    """Clean filename by removing invalid characters"""
    # Remove invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    # Remove leading/trailing underscores
    cleaned = cleaned.strip('_')
    return cleaned


def parse_log_level(level: str) -> int:
    """Parse log level to numeric value for sorting"""
    level_map = {
        'TRACE': 0,
        'DEBUG': 1,
        'INFO': 2,
        'WARN': 3,
        'WARNING': 3,
        'ERROR': 4,
        'FATAL': 5,
        'CRITICAL': 5
    }
    return level_map.get(level.upper(), 2)  # Default to INFO


def is_valid_email(email: str) -> bool:
    """Check if email is valid"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def is_valid_url(url: str) -> bool:
    """Check if URL is valid"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None


def group_by_key(items: List[Dict], key: str) -> Dict[str, List[Dict]]:
    """Group list of dictionaries by a key"""
    grouped = {}
    for item in items:
        group_key = item.get(key, 'unknown')
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    return grouped


def sort_by_key(items: List[Dict], key: str, reverse: bool = False) -> List[Dict]:
    """Sort list of dictionaries by a key"""
    return sorted(items, key=lambda x: x.get(key, ''), reverse=reverse)


def get_redis_client() -> redis.Redis:
    """Get Redis client instance"""
    try:
        return redis.from_url(settings.REDIS_URL)
    except Exception as e:
        # Return None if Redis is not available
        return None

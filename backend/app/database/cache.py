"""
Redis caching strategy for expensive database queries
Intelligent caching with TTL and invalidation
"""

import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis.asyncio as redis
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class DatabaseCache:
    """Redis-based caching for database queries"""
    
    def __init__(self):
        self.redis_client = None
        self.cache_prefix = "loglytics:db:"
        self.default_ttl = 300  # 5 minutes
        self.long_ttl = 3600   # 1 hour
        self.short_ttl = 60    # 1 minute
        
        # Cache key patterns
        self.key_patterns = {
            "user_profile": f"{self.cache_prefix}user:{{user_id}}:profile",
            "user_projects": f"{self.cache_prefix}user:{{user_id}}:projects",
            "project_analytics": f"{self.cache_prefix}project:{{project_id}}:analytics",
            "log_stats": f"{self.cache_prefix}project:{{project_id}}:log_stats",
            "error_patterns": f"{self.cache_prefix}project:{{project_id}}:error_patterns",
            "usage_tracking": f"{self.cache_prefix}user:{{user_id}}:usage",
            "audit_logs": f"{self.cache_prefix}user:{{user_id}}:audit_logs",
            "rag_vectors": f"{self.cache_prefix}project:{{project_id}}:vectors",
            "subscription_limits": f"{self.cache_prefix}user:{{user_id}}:limits"
        }
    
    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                password=settings.REDIS_PASSWORD,
                decode_responses=False,  # We'll handle encoding ourselves
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            await self.redis_client.ping()
            logger.info("Redis cache initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Redis cache: {e}")
            return False
    
    def _generate_cache_key(self, pattern: str, **kwargs) -> str:
        """Generate cache key from pattern and parameters"""
        try:
            return pattern.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing parameter for cache key pattern {pattern}: {e}")
            return f"{self.cache_prefix}error:{hashlib.md5(str(kwargs).encode()).hexdigest()}"
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for caching"""
        try:
            # Use pickle for complex objects, JSON for simple data
            if isinstance(data, (dict, list, str, int, float, bool, type(None))):
                return json.dumps(data, default=str).encode('utf-8')
            else:
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"Error serializing data: {e}")
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize cached data"""
        try:
            # Try JSON first, fallback to pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        except Exception as e:
            logger.error(f"Error deserializing data: {e}")
            return None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get data from cache"""
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return None
            
            return self._deserialize_data(data)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        data: Any, 
        ttl: Optional[int] = None,
        nx: bool = False
    ) -> bool:
        """Set data in cache with TTL"""
        if not self.redis_client:
            return False
        
        try:
            serialized_data = self._serialize_data(data)
            ttl = ttl or self.default_ttl
            
            if nx:
                # Only set if key doesn't exist
                result = await self.redis_client.set(key, serialized_data, ex=ttl, nx=True)
            else:
                result = await self.redis_client.set(key, serialized_data, ex=ttl)
            
            return result is not None
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete data from cache"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func, 
        ttl: Optional[int] = None,
        *args, 
        **kwargs
    ) -> Any:
        """Get from cache or fetch and set"""
        # Try to get from cache first
        cached_data = await self.get(key)
        if cached_data is not None:
            return cached_data
        
        # Fetch data if not in cache
        try:
            data = await fetch_func(*args, **kwargs)
            if data is not None:
                await self.set(key, data, ttl)
            return data
        except Exception as e:
            logger.error(f"Error in get_or_set for key {key}: {e}")
            return None
    
    # Specific cache methods for common queries
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from cache"""
        key = self._generate_cache_key(self.key_patterns["user_profile"], user_id=user_id)
        return await self.get(key)
    
    async def set_user_profile(self, user_id: str, profile: Dict[str, Any]) -> bool:
        """Set user profile in cache"""
        key = self._generate_cache_key(self.key_patterns["user_profile"], user_id=user_id)
        return await self.set(key, profile, self.long_ttl)
    
    async def invalidate_user_profile(self, user_id: str) -> bool:
        """Invalidate user profile cache"""
        key = self._generate_cache_key(self.key_patterns["user_profile"], user_id=user_id)
        return await self.delete(key)
    
    async def get_user_projects(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get user projects from cache"""
        key = self._generate_cache_key(self.key_patterns["user_projects"], user_id=user_id)
        return await self.get(key)
    
    async def set_user_projects(self, user_id: str, projects: List[Dict[str, Any]]) -> bool:
        """Set user projects in cache"""
        key = self._generate_cache_key(self.key_patterns["user_projects"], user_id=user_id)
        return await self.set(key, projects, self.default_ttl)
    
    async def invalidate_user_projects(self, user_id: str) -> bool:
        """Invalidate user projects cache"""
        key = self._generate_cache_key(self.key_patterns["user_projects"], user_id=user_id)
        return await self.delete(key)
    
    async def get_project_analytics(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project analytics from cache"""
        key = self._generate_cache_key(self.key_patterns["project_analytics"], project_id=project_id)
        return await self.get(key)
    
    async def set_project_analytics(self, project_id: str, analytics: Dict[str, Any]) -> bool:
        """Set project analytics in cache"""
        key = self._generate_cache_key(self.key_patterns["project_analytics"], project_id=project_id)
        return await self.set(key, analytics, self.default_ttl)
    
    async def invalidate_project_analytics(self, project_id: str) -> bool:
        """Invalidate project analytics cache"""
        key = self._generate_cache_key(self.key_patterns["project_analytics"], project_id=project_id)
        return await self.delete(key)
    
    async def get_log_stats(self, project_id: str) -> Optional[Dict[str, int]]:
        """Get log statistics from cache"""
        key = self._generate_cache_key(self.key_patterns["log_stats"], project_id=project_id)
        return await self.get(key)
    
    async def set_log_stats(self, project_id: str, stats: Dict[str, int]) -> bool:
        """Set log statistics in cache"""
        key = self._generate_cache_key(self.key_patterns["log_stats"], project_id=project_id)
        return await self.set(key, stats, self.short_ttl)
    
    async def get_error_patterns(self, project_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get error patterns from cache"""
        key = self._generate_cache_key(self.key_patterns["error_patterns"], project_id=project_id)
        return await self.get(key)
    
    async def set_error_patterns(self, project_id: str, patterns: List[Dict[str, Any]]) -> bool:
        """Set error patterns in cache"""
        key = self._generate_cache_key(self.key_patterns["error_patterns"], project_id=project_id)
        return await self.set(key, patterns, self.default_ttl)
    
    async def get_usage_tracking(self, user_id: str, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """Get usage tracking data from cache"""
        key = f"{self.cache_prefix}user:{user_id}:usage:{start_date}:{end_date}"
        return await self.get(key)
    
    async def set_usage_tracking(
        self, 
        user_id: str, 
        start_date: str, 
        end_date: str, 
        data: List[Dict[str, Any]]
    ) -> bool:
        """Set usage tracking data in cache"""
        key = f"{self.cache_prefix}user:{user_id}:usage:{start_date}:{end_date}"
        return await self.set(key, data, self.default_ttl)
    
    async def get_audit_logs(
        self, 
        user_id: str, 
        action: Optional[str] = None,
        page: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Get audit logs from cache"""
        key = f"{self.cache_prefix}user:{user_id}:audit_logs:{action or 'all'}:{page}"
        return await self.get(key)
    
    async def set_audit_logs(
        self, 
        user_id: str, 
        action: Optional[str], 
        page: int, 
        data: Dict[str, Any]
    ) -> bool:
        """Set audit logs in cache"""
        key = f"{self.cache_prefix}user:{user_id}:audit_logs:{action or 'all'}:{page}"
        return await self.set(key, data, self.default_ttl)
    
    async def invalidate_user_cache(self, user_id: str) -> int:
        """Invalidate all cache entries for a user"""
        pattern = f"{self.cache_prefix}user:{user_id}:*"
        return await self.delete_pattern(pattern)
    
    async def invalidate_project_cache(self, project_id: str) -> int:
        """Invalidate all cache entries for a project"""
        pattern = f"{self.cache_prefix}project:{project_id}:*"
        return await self.delete_pattern(pattern)
    
    async def warm_cache(self, user_id: str):
        """Warm cache with frequently accessed data"""
        try:
            # This would be called during user login or system startup
            # to pre-populate frequently accessed data
            
            # Warm user profile cache
            from app.database.queries import OptimizedQueries
            from app.database import get_db
            
            async for session in get_db():
                queries = OptimizedQueries(session)
                
                # Cache user profile
                user_profile = await queries.get_user_with_projects_and_recent_chats(user_id)
                if user_profile:
                    await self.set_user_profile(user_id, user_profile)
                
                # Cache user projects
                if user_profile and "projects" in user_profile:
                    await self.set_user_projects(user_id, user_profile["projects"])
                
                break
            
            logger.info(f"Cache warmed for user {user_id}")
        except Exception as e:
            logger.error(f"Error warming cache for user {user_id}: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"status": "not_connected"}
        
        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human", "0B"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)) * 100
                )
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"status": "error", "error": str(e)}
    
    async def clear_all_cache(self) -> bool:
        """Clear all cache data"""
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.flushdb()
            logger.info("All cache data cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis cache connection closed")

# Global cache instance
db_cache = DatabaseCache()

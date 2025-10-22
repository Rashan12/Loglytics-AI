"""
Redis client with optional availability
Handles Redis connection gracefully when Redis is not available
"""

import redis.asyncio as redis
from app.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client with optional availability"""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
        self._available = False
        self._try_connect()
    
    def _try_connect(self):
        """Try to connect to Redis"""
        try:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            # Test connection with a simple ping
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, we can't use run_until_complete
                # We'll test the connection later when we actually use it
                self._available = True
                logger.info("Redis client initialized (connection will be tested on first use)")
            else:
                loop.run_until_complete(self._test_connection())
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}. Continuing without Redis.")
            self._available = False
            self._client = None
    
    async def _test_connection(self):
        """Test Redis connection"""
        try:
            await self._client.ping()
            self._available = True
            logger.info("Redis connected successfully")
        except Exception as e:
            logger.warning(f"Redis connection test failed: {e}. Continuing without Redis.")
            self._available = False
            self._client = None
    
    async def ensure_connection(self):
        """Ensure Redis connection is available"""
        if not self._available and self._client:
            await self._test_connection()
        return self._available
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._available
    
    def get_client(self) -> Optional[redis.Redis]:
        """Get Redis client if available"""
        return self._client if self._available else None
    
    async def ping(self) -> bool:
        """Ping Redis server"""
        try:
            if self._client and self._available:
                await self._client.ping()
                return True
        except Exception as e:
            logger.warning(f"Redis ping failed: {e}")
            self._available = False
        return False
    
    async def execute_command(self, command: str, *args, **kwargs):
        """Execute Redis command safely"""
        try:
            if not await self.ensure_connection():
                return None
            
            if command == "get":
                return await self._client.get(*args, **kwargs)
            elif command == "set":
                return await self._client.set(*args, **kwargs)
            elif command == "setex":
                return await self._client.setex(*args, **kwargs)
            elif command == "delete":
                return await self._client.delete(*args, **kwargs)
            elif command == "incr":
                return await self._client.incr(*args, **kwargs)
            elif command == "expire":
                return await self._client.expire(*args, **kwargs)
            elif command == "keys":
                return await self._client.keys(*args, **kwargs)
            elif command == "sadd":
                return await self._client.sadd(*args, **kwargs)
            elif command == "smembers":
                return await self._client.smembers(*args, **kwargs)
            elif command == "srem":
                return await self._client.srem(*args, **kwargs)
            elif command == "zadd":
                return await self._client.zadd(*args, **kwargs)
            elif command == "zcard":
                return await self._client.zcard(*args, **kwargs)
            elif command == "zremrangebyscore":
                return await self._client.zremrangebyscore(*args, **kwargs)
            elif command == "zrange":
                return await self._client.zrange(*args, **kwargs)
            elif command == "ttl":
                return await self._client.ttl(*args, **kwargs)
            else:
                # Generic command execution
                return await getattr(self._client, command)(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Redis command '{command}' failed: {e}")
            return None

# Global Redis client instance
redis_client = RedisClient()

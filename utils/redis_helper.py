import redis
import os
from utils import app_logger

class RedisHelper:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        self.redis_password = os.getenv('REDIS_PASSWORD', None)
        
        try:
            self.client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True
            )
            # Test connection
            self.client.ping()
        except Exception as e:
            app_logger.exceptionlogs(f"Redis connection failed: {e}")
            self.client = None

    def set_with_ttl(self, key: str, value: str, ttl: int):
        """Set a key-value pair with TTL (time to live) in seconds"""
        try:
            if self.client:
                return self.client.setex(key, ttl, value)
            return False
        except Exception as e:
            app_logger.exceptionlogs(f"Error setting Redis key {key}: {e}")
            return False

    def get(self, key: str):
        """Get value by key"""
        try:
            if self.client:
                return self.client.get(key)
            return None
        except Exception as e:
            app_logger.exceptionlogs(f"Error getting Redis key {key}: {e}")
            return None

    def delete(self, key: str):
        """Delete a key"""
        try:
            if self.client:
                return self.client.delete(key)
            return False
        except Exception as e:
            app_logger.exceptionlogs(f"Error deleting Redis key {key}: {e}")
            return False

    def exists(self, key: str):
        """Check if key exists"""
        try:
            if self.client:
                return self.client.exists(key)
            return False
        except Exception as e:
            app_logger.exceptionlogs(f"Error checking Redis key {key}: {e}")
            return False

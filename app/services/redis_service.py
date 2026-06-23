# app/services/redis_service.py
# Unified async Redis client — re-exports from app.cache.redis

from app.cache.redis import redis_client

__all__ = ["redis_client"]

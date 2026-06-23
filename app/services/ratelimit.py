# app/services/ratelimit.py

from app.cache.redis import redis_client

WINDOW = 60
LIMIT = 100


async def api_limit(ip: str) -> bool:
    key = f"api:{ip}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, WINDOW)
    return count <= LIMIT

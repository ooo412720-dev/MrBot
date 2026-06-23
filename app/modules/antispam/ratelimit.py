# app/modules/antispam/ratelimit.py

from app.cache.redis import redis_client

LIMIT = 10
WINDOW = 15


async def flood_detected(group_id: int, user_id: int) -> tuple[bool, int]:
    key = f"flood:{group_id}:{user_id}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, WINDOW)
    return (count >= LIMIT, count)

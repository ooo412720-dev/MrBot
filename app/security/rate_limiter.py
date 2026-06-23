# app/security/rate_limiter.py

import time

from app.cache.redis import redis_client


LIMIT = 5
WINDOW = 10


async def check_rate_limit(

        user_id: int

):

    key = f"rate:{user_id}"

    current = await redis_client.get(key)

    if current:

        if int(current) >= LIMIT:
            return False

        await redis_client.incr(key)

        return True

    await redis_client.set(
        key,
        1,
        ex=WINDOW
    )

    return True
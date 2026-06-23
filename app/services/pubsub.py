# app/services/pubsub.py

from app.cache.redis import redis_client


async def publish(channel: str, message: str):
    await redis_client.publish(channel, message)

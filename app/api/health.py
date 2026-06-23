# app/api/health.py

from sqlalchemy import text
from fastapi import APIRouter
from app.cache.redis import redis_client
from app.database.session import engine
from app.bot.bot import bot


router = APIRouter()


async def check_health():
    db_ok = False
    redis_ok = False
    telegram = False

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    try:
        await redis_client.ping()
        redis_ok = True
    except Exception:
        pass

    try:
        me = await bot.get_me()
        if me:
            telegram = True
    except Exception:
        pass

    return {
        "postgres": db_ok,
        "redis": redis_ok,
        "telegram": telegram
    }

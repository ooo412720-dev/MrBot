# app/core/lifecycle.py

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.cache.redis import redis_client
from app.database.session import engine
from app.core.module_loader import load_modules
from app.core.logger import logger
from app.core.security import validate_environment
from app.bot.register import register_handlers
from app.bot.setup import setup_middlewares
from app.services.scheduler import start_scheduler

bot_task: Optional[asyncio.Task] = None


async def start_database() -> None:
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: engine.connect().close()
        )
        logger.info("PostgreSQL connected successfully")
    except SQLAlchemyError as e:
        logger.exception(f"Database startup failed: {e}")
        raise RuntimeError("Cannot connect to PostgreSQL")


async def start_redis() -> None:
    try:
        await redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.exception(f"Redis startup failed: {e}")
        raise RuntimeError("Cannot connect to Redis")


async def start_telegram() -> asyncio.Task:
    try:
        task = asyncio.create_task(
            dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types()
            )
        )
        logger.info("Telegram polling started")
        return task
    except Exception as e:
        logger.exception(f"Telegram startup failed: {e}")
        raise RuntimeError("Cannot start telegram bot")


async def shutdown_telegram() -> None:
    try:
        await bot.session.close()
        logger.info("Telegram session closed")
    except Exception as e:
        logger.exception(f"Telegram shutdown error: {e}")


async def shutdown_redis() -> None:
    try:
        await redis_client.close()
        logger.info("Redis closed")
    except Exception as e:
        logger.exception(f"Redis shutdown error: {e}")


async def shutdown_database() -> None:
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, engine.dispose)
        logger.info("PostgreSQL engine disposed")
    except Exception as e:
        logger.exception(f"Database shutdown error: {e}")


async def cancel_bot_task() -> None:
    global bot_task
    if bot_task:
        try:
            bot_task.cancel()
            await bot_task
        except asyncio.CancelledError:
            logger.info("Telegram polling stopped")
        except Exception as e:
            logger.exception(f"Task cancellation error: {e}")


@asynccontextmanager
async def lifespan(app):
    global bot_task

    logger.info("========== APPLICATION STARTING ==========")

    try:
        validate_environment()
        logger.info("Environment validated")

        await start_database()
        await start_redis()

        load_modules()
        logger.info("Modules loaded successfully")

        register_handlers()
        logger.info("Handlers registered")

        setup_middlewares()
        logger.info("Middlewares initialized")

        start_scheduler()
        logger.info("Scheduler started")

        bot_task = await start_telegram()
        logger.info("Application startup completed")

        yield

    except Exception as startup_error:
        logger.exception(f"STARTUP FAILED: {startup_error}")
        raise

    finally:
        logger.info("========== SHUTDOWN STARTED ==========")
        await cancel_bot_task()
        await shutdown_telegram()
        await shutdown_redis()
        await shutdown_database()
        logger.info("Shutdown completed successfully")

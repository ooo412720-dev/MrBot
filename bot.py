# bot.py
# نقطة دخول لتشغيل البوت مباشرة

import asyncio
import sys
from pathlib import Path

from aiogram.types import FSInputFile, InputProfilePhotoStatic

from app.core.logger import logger
from app.core.security import validate_environment
from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.register import register_handlers
from app.bot.setup import setup_middlewares

BOOT_IMAGE = Path(__file__).resolve().parent / "boot.jpg"


async def main():
    logger.info("========== MRBOT STARTING ==========")

    validate_environment()
    logger.info("Environment validated")

    from app.database.session import async_engine
    from app.database.base import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    if BOOT_IMAGE.exists():
        try:
            await bot.delete_my_photo()
        except Exception:
            pass
        try:
            photo = FSInputFile(BOOT_IMAGE)
            await bot.set_my_profile_photo(
                photo=InputProfilePhotoStatic(photo=photo)
            )
            logger.info("Bot profile photo updated")
        except Exception as e:
            logger.warning(f"Could not set profile photo: {e}")

    register_handlers()
    logger.info("Handlers registered")

    setup_middlewares()
    logger.info("Middlewares initialized")

    try:
        from app.services.scheduler import start_scheduler
        start_scheduler()
        logger.info("Scheduler started")
    except Exception as e:
        logger.warning(f"Scheduler not started: {e}")

    me = await bot.get_me()
    logger.info(f"Bot started: @{me.username}")

    await bot.set_my_commands([
        {"command": "start", "description": "بدء البوت"},
        {"command": "help", "description": "قائمة الأوامر"},
        {"command": "ping", "description": "فحص البوت"},
        {"command": "id", "description": "معلومات الحساب"},
        {"command": "rules", "description": "قوانين الجروب"},
        {"command": "settings", "description": "إعدادات الجروب"},
    ])

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
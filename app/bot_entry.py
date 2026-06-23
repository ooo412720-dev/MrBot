# app/bot_entry.py
# نقطة دخول لتشغيل البوت مباشرة بدون FastAPI

import asyncio
import sys
from pathlib import Path

from aiogram.types import FSInputFile

from app.core.logger import logger
from app.core.security import validate_environment
from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.register import register_handlers
from app.bot.setup import setup_middlewares
from app.bot.errors import global_error_handler

BOOT_IMAGE = Path(__file__).resolve().parent / "boot.jpg"


async def main():
    logger.info("========== MRBOT STARTING ==========")

    validate_environment()
    logger.info("Environment validated")

    if BOOT_IMAGE.exists():
        try:
            await bot.delete_my_photo()
            logger.info("Old profile photo deleted")
        except Exception:
            pass

        try:
            photo = FSInputFile(BOOT_IMAGE)
            await bot.set_my_profile_photo(photo=photo)
            logger.info("Bot profile photo updated")
        except Exception as e:
            logger.warning(f"Could not set profile photo: {e}")
    else:
        logger.warning(f"boot.jpg not found at {BOOT_IMAGE}")

    register_handlers()
    logger.info("Handlers registered")

    setup_middlewares()
    logger.info("Middlewares initialized")

    me = await bot.get_me()
    logger.info(f"Bot started: @{me.username}")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
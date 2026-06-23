# app/services/watchdog.py

import asyncio

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.core.logger import logger


async def bot_watchdog():
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.exception(f"Polling stopped: {e}")
            await asyncio.sleep(10)

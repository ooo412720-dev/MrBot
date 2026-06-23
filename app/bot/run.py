# app/bot/run.py

import asyncio

from app.bot.bot import bot
from app.bot.dispatcher import dp
from app.bot.register import register_handlers
from app.bot.setup import setup_middlewares
from app.bot.errors import global_error_handler


async def start_bot():
    register_handlers()
    setup_middlewares()
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(start_bot())

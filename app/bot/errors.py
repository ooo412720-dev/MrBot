# app/bot/errors.py

from aiogram.types import ErrorEvent

from app.bot.dispatcher import dp
from app.core.logger import logger


@dp.errors()
async def global_error_handler(
        event: ErrorEvent
):

    logger.exception(
        f"Telegram Error: "
        f"{event.exception}"
    )

    return True
# app/bot/middlewares.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.core.logger import logger


class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        text = None

        if isinstance(event, (Message, CallbackQuery)):
            if event.from_user:
                user_id = event.from_user.id
            if isinstance(event, Message):
                text = event.text
            elif isinstance(event, CallbackQuery):
                text = event.data

        logger.info(f"USER={user_id} TEXT={text}")
        return await handler(event, data)

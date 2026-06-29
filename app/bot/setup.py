from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

from app.bot.dispatcher import dp
from app.bot.bot import bot
from app.core.logger import logger


class GroupCommandMiddleware(BaseMiddleware):
    """Middleware لمعالجة الأوامر مع @mention في المجموعات"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        if event.text and event.text.startswith('/'):
            parts = event.text.split('@', 1)
            command = parts[0]

            if len(parts) > 1:
                mentioned_username = parts[1].strip()
                me = await bot.get_me()

                if mentioned_username.lower() != me.username.lower():
                    return None

                event.text = command

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Middleware لتسجيل الأوامر"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        if event.text and event.text.startswith('/'):
            chat_type = event.chat.type if event.chat else "unknown"
            username = event.from_user.username if event.from_user else "unknown"
            logger.info(
                f"Command: {event.text} | "
                f"User: {event.from_user.id} (@{username}) | "
                f"Chat: {event.chat.id if event.chat else 'N/A'} ({chat_type})"
            )

        return await handler(event, data)


class GroupRegistrationMiddleware(BaseMiddleware):
    """Middleware لتسجيل الجروبات تلقائياً"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:

        if event.chat and event.chat.type in ("group", "supergroup"):
            try:
                from app.database.db import get_or_create_group_settings
                await get_or_create_group_settings(event.chat.id, event.chat.title)
            except Exception as e:
                logger.warning(f"Failed to register group: {e}")

        return await handler(event, data)


def setup_middlewares():
    dp.message.middleware(GroupRegistrationMiddleware())
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(GroupCommandMiddleware())
    logger.info("All middlewares registered successfully")

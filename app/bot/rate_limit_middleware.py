# app/bot/rate_limit_middleware.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.security.rate_limiter import check_rate_limit


class RateLimitMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = None
        if isinstance(event, (Message, CallbackQuery)):
            if event.from_user:
                user_id = event.from_user.id

        if user_id:
            allowed = await check_rate_limit(user_id)
            if not allowed:
                if isinstance(event, Message):
                    await event.answer("Too many requests.")
                elif isinstance(event, CallbackQuery):
                    await event.answer("Too many requests.", show_alert=True)
                return

        return await handler(event, data)

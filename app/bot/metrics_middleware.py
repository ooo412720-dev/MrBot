# app/bot/metrics_middleware.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from app.monitoring.metrics import MESSAGES_COUNTER


class MetricsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        MESSAGES_COUNTER.inc()
        return await handler(event, data)

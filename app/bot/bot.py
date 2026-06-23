# app/bot/bot.py

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings


bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode="HTML"
    )
)
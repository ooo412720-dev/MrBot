# app/bot/bot.py

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings

# إنشاء البوت بدون parse_mode (لحل مشكلة Markdown)
bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=None)
)

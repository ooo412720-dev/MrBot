from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=None))

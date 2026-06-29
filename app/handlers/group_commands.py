# app/handlers/group_commands.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.logger import logger

router = Router()


@router.message(Command("start"))
async def group_start_handler(message: Message):
    """معالج /start في المجموعات"""
    if message.chat.type not in ("group", "supergroup"):
        return
    
    from app.database.db import get_or_create_group_settings, get_or_create_user
    
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )
    
    await get_or_create_group_settings(message.chat.id, message.chat.title)
    
    await message.answer(
        f"✅ تم تسجيل الجروب: {message.chat.title}\n"
        f"🤖 MrBot جاهز للعمل!\n"
        f"أرسل /help لعرض الأوامر المتاحة."
    )

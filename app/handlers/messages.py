# app/handlers/messages.py

from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text)
async def catch_all(message: Message):
    await message.answer(f"📝 {message.text}")

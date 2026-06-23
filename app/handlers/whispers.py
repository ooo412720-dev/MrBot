# app/handlers/whispers.py

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Bot

from app.bot.bot import bot

router = Router()


@router.message(Command("whisper"))
async def whisper_handler(message: Message):
    """
    إرسال همسة لشخص في المجموعة
    الاستخدام: رد على رسالة الشخص واكتب /whisper رسالتك
    أو: /whisper @username رسالتك
    """
    if not message.reply_to_message:
        await message.answer(
            "📋 طريقة الاستخدام:\n"
            "1. رد على رسالة الشخص واكتب: /whisper رسالتك\n"
            "2. أو اكتب: /whisper @username رسالتك"
        )
        return

    target = message.reply_to_message.from_user
    sender = message.from_user

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ اكتب الرسالة بعد الأمر.\nمثال: /whisper مرحباً كيف حالك")
        return

    whisper_text = args[1]

    if sender.id == target.id:
        await message.answer("⚠️ لا يمكنك إرسال همسة لنفسك.")
        return

    try:
        await bot.send_message(
            target.id,
            f"📩 همسة خاصة من {sender.full_name}:\n\n{whisper_text}"
        )
        await message.answer("✅ تم إرسال الهمسة بنجاح.")
    except Exception:
        await message.answer("❌ تعذر إرسال الهمسة. قد يكون المستخدم قد حظر البوت.")

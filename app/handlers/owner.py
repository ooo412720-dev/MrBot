# app/handlers/owner.py

from pathlib import Path

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile, InputProfilePhotoStatic

from app.core.config import settings
from app.core.logger import logger
from app.bot.bot import bot

router = Router()


def is_owner(user_id: int) -> bool:
    return user_id == settings.OWNER_ID


@router.message(Command("setphoto"))
async def set_bot_photo(message: Message):
    if not is_owner(message.from_user.id):
        return

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("رد على صورة وارسل /setphoto لتعيينها كصورة بروفايل للبوت.")
        return

    try:
        file_id = message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        downloaded = await bot.download_file(file.file_path)
        photo = FSInputFile(downloaded)
        await bot.delete_my_photo()
        await bot.set_my_profile_photo(
            photo=InputProfilePhotoStatic(photo=photo)
        )
        await message.answer("✅ تم تغيير صورة البوت.")
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")


@router.message(Command("setname"))
async def set_bot_name(message: Message, command: CommandObject):
    if not is_owner(message.from_user.id):
        return

    name = command.args
    if not name:
        await message.reply("اكتب الاسم بعد الأمر.\nمثال: /setname Mr Bot")
        return

    try:
        await bot.set_my_name(name)
        await message.answer(f"✅ تم تغيير اسم البوت إلى: {name}")
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")


@router.message(Command("setdesc"))
async def set_bot_desc(message: Message, command: CommandObject):
    if not is_owner(message.from_user.id):
        return

    desc = command.args
    if not desc:
        await message.reply("اكتب الوصف بعد الأمر.\nمثال: /setdesc بوت إدارة المجموعات")
        return

    try:
        await bot.set_my_description(description=desc)
        await message.answer(f"✅ تم تغيير وصف البوت إلى:\n{desc}")
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")


@router.message(Command("setabout"))
async def set_bot_about(message: Message, command: CommandObject):
    if not is_owner(message.from_user.id):
        return

    about = command.args
    if not about:
        await message.reply("اكتب النبذة بعد الأمر.\nمثال: /setabout بوت لإدارة الجروبات")
        return

    try:
        await bot.set_my_short_description(short_description=about)
        await message.answer(f"✅ تم تغيير نبذة البوت إلى:\n{about}")
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")


@router.message(Command("botinfo"))
async def bot_info(message: Message):
    if not is_owner(message.from_user.id):
        return

    try:
        me = await bot.get_me()
        text = (
            f"🤖 **معلومات البوت**\n\n"
            f"📛 الاسم: {me.full_name}\n"
            f"👤 المعرف: @{me.username}\n"
            f"🆔 ID: `{me.id}`\n"
            f"🔗 الرابط: https://t.me/{me.username}\n\n"
            f"📋 **الأوامر المتاحة لك:**\n"
            f"• /setphoto — تغيير صورة البوت (رد على صورة)\n"
            f"• /setname <name> — تغيير اسم البوت\n"
            f"• /setdesc <text> — تغيير وصف البوت\n"
            f"• /setabout <text> — تغيير نبذة البوت\n"
            f"• /botinfo — عرض معلومات البوت\n"
            f"• /broadcast <text> — إرسال رسالة لكل المجموعات\n"
        )
        await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}")


@router.message(Command("broadcast"))
async def broadcast(message: Message, command: CommandObject):
    if not is_owner(message.from_user.id):
        return

    text = command.args
    if not text:
        await message.reply("اكتب الرسالة بعد الأمر.\nمثال: /broadcast مرحباً للجميع")
        return

    from app.database.db import get_all_groups
    groups = await get_all_groups()

    if not groups:
        await message.answer("لا توجد مجموعات مسجلة.")
        return

    sent = 0
    failed = 0
    for g in groups:
        try:
            await bot.send_message(g.group_id, f"📢 **إعلان من المالك:**\n\n{text}")
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📊 **نتيجة الإرسال:**\n\n"
        f"✅ نجح: {sent}\n"
        f"❌ فشل: {failed}\n"
        f"📋 المجموع: {len(groups)}"
    )

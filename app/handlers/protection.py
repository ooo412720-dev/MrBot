# app/handlers/protection.py

import re
from collections import defaultdict
from time import time

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions

from app.bot.bot import bot
from app.database.db import get_or_create_group_settings, update_group_setting, add_log

router = Router()

URL_PATTERN = re.compile(r"(https?://|t\.me/|www\.)", re.IGNORECASE)

spam_cache: dict[int, list[float]] = defaultdict(list)
SPAM_LIMIT = 5
SPAM_WINDOW = 10

raid_cache: dict[int, list[float]] = defaultdict(list)
RAID_LIMIT = 10
RAID_WINDOW = 60


@router.message(Command("antilink"))
async def toggle_antilink(message: Message):
    if not message.from_user.is_chat_admin():
        return

    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.antilink_enabled
    await update_group_setting(message.chat.id, "antilink_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"🔗 حظر الروابط: {status}")


@router.message(Command("antispam"))
async def toggle_antispam(message: Message):
    if not message.from_user.is_chat_admin():
        return

    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.antispam_enabled
    await update_group_setting(message.chat.id, "antispam_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"🛡️ مكافحة السبام: {status}")


@router.message(Command("lock"))
async def lock_media(message: Message, command):
    if not message.from_user.is_chat_admin():
        return

    lock_type = (command.args or "").lower().strip()
    settings = await get_or_create_group_settings(message.chat.id)

    if lock_type in ("media", "photos", "صور"):
        await update_group_setting(message.chat.id, "lock_media", True)
        await message.answer("🔒 تم قفل الصور والوسائط.")
    elif lock_type in ("stickers", "ملصقات"):
        await update_group_setting(message.chat.id, "lock_stickers", True)
        await message.answer("🔒 تم قفل الملصقات.")
    elif lock_type in ("forward", "توجيه"):
        await update_group_setting(message.chat.id, "lock_forward", True)
        await message.answer("🔒 تم قفل التوجيه.")
    elif lock_type in ("all", "الكل"):
        await update_group_setting(message.chat.id, "lock_media", True)
        await update_group_setting(message.chat.id, "lock_stickers", True)
        await update_group_setting(message.chat.id, "lock_forward", True)
        await message.answer("🔒 تم قفل كل الوسائط.")
    else:
        await message.reply(
            "📝 الاستخدام: /lock <type>\n\n"
            "الأنواع: media, stickers, forward, all"
        )


@router.message(Command("unlock"))
async def unlock_media(message: Message, command):
    if not message.from_user.is_chat_admin():
        return

    lock_type = (command.args or "").lower().strip()

    if lock_type in ("media", "photos", "صور"):
        await update_group_setting(message.chat.id, "lock_media", False)
        await message.answer("🔓 تم فتح الصور والوسائط.")
    elif lock_type in ("stickers", "ملصقات"):
        await update_group_setting(message.chat.id, "lock_stickers", False)
        await message.answer("🔓 تم فتح الملصقات.")
    elif lock_type in ("forward", "توجيه"):
        await update_group_setting(message.chat.id, "lock_forward", False)
        await message.answer("🔓 تم فتح التوجيه.")
    elif lock_type in ("all", "الكل"):
        await update_group_setting(message.chat.id, "lock_media", False)
        await update_group_setting(message.chat.id, "lock_stickers", False)
        await update_group_setting(message.chat.id, "lock_forward", False)
        await message.answer("🔓 تم فتح كل الوسائط.")
    else:
        await message.reply(
            "📝 الاستخدام: /unlock <type>\n\n"
            "الأنواع: media, stickers, forward, all"
        )


@router.message(F.text)
async def check_protection(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if message.from_user.is_bot:
        return

    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("creator", "administrator"):
            return
    except Exception:
        return

    settings = await get_or_create_group_settings(message.chat.id)

    if settings.antilink_enabled and message.text:
        if URL_PATTERN.search(message.text):
            try:
                await message.delete()
                await message.answer(
                    f"🚫 {message.from_user.full_name}، الروابط ممنوعة!"
                )
                return
            except Exception:
                pass

    if settings.antispam_enabled and message.text:
        now = time()
        user_id = message.from_user.id
        spam_cache[user_id].append(now)
        spam_cache[user_id] = [t for t in spam_cache[user_id] if now - t <= SPAM_WINDOW]

        if len(spam_cache[user_id]) >= SPAM_LIMIT:
            try:
                permissions = ChatPermissions(can_send_messages=False)
                await bot.restrict_chat_member(
                    message.chat.id, user_id, permissions
                )
                await message.answer(
                    f"🔇 تم كتم {message.from_user.full_name} بسبب السبام."
                )
                await add_log(message.chat.id, user_id, "auto_mute_spam")
                spam_cache[user_id] = []
            except Exception:
                pass


@router.message(F.sticker)
async def check_sticker_lock(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if message.from_user.is_bot:
        return

    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("creator", "administrator"):
            return
    except Exception:
        return

    settings = await get_or_create_group_settings(message.chat.id)
    if settings.lock_stickers:
        try:
            await message.delete()
        except Exception:
            pass


@router.message(F.photo | F.video | F.audio | F.document | F.animation)
async def check_media_lock(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if message.from_user.is_bot:
        return

    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("creator", "administrator"):
            return
    except Exception:
        return

    settings = await get_or_create_group_settings(message.chat.id)
    if settings.lock_media:
        try:
            await message.delete()
        except Exception:
            pass


@router.message(F.forward_date)
async def check_forward_lock(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if message.from_user.is_bot:
        return

    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ("creator", "administrator"):
            return
    except Exception:
        return

    settings = await get_or_create_group_settings(message.chat.id)
    if settings.lock_forward:
        try:
            await message.delete()
        except Exception:
            pass

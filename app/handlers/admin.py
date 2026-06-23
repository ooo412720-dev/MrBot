# app/handlers/admin.py

from datetime import datetime, timedelta, timezone

from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ChatPermissions
from aiogram.exceptions import TelegramBadRequest

from app.bot.bot import bot
from app.database.db import (
    add_warning, clear_warnings, get_warnings_count, add_log
)

router = Router()


def parse_duration(text: str) -> int | None:
    """تحليل المدة من نص: 1h, 30m, 2d"""
    if not text:
        return None
    text = text.lower().strip()
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    for unit, multiplier in units.items():
        if text.endswith(unit):
            try:
                num = int(text[:-1])
                return num * multiplier
            except ValueError:
                return None
    try:
        return int(text) * 60
    except ValueError:
        return None


@router.message(Command("ban"))
async def ban_user(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد حظره.")
        return

    target = message.reply_to_message.from_user
    reason = command.args or "بدون سبب"

    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await message.answer(
            f"🚫 **تم حظر العضو**\n\n"
            f"👤 الاسم: {target.full_name}\n"
            f"🆔 ID: `{target.id}`\n"
            f"📝 السبب: {reason}"
        )
        await add_log(message.chat.id, message.from_user.id, f"ban {target.id}: {reason}")
    except TelegramBadRequest:
        await message.answer("❌ لا يمكنني حظر هذا العضو. تأكد من أنني مشرف.")


@router.message(Command("unban"))
async def unban_user(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد رفع حظره.")
        return

    target = message.reply_to_message.from_user

    try:
        await bot.unban_chat_member(message.chat.id, target.id, only_if_banned=True)
        await message.answer(f"✅ تم رفع الحظر عن {target.full_name}")
        await add_log(message.chat.id, message.from_user.id, f"unban {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ تعذر رفع الحظر.")


@router.message(Command("kick"))
async def kick_user(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد طرده.")
        return

    target = message.reply_to_message.from_user
    reason = command.args or "بدون سبب"

    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await bot.unban_chat_member(message.chat.id, target.id, only_if_banned=True)
        await message.answer(
            f"👢 **تم طرد العضو**\n\n"
            f"👤 الاسم: {target.full_name}\n"
            f"📝 السبب: {reason}"
        )
        await add_log(message.chat.id, message.from_user.id, f"kick {target.id}: {reason}")
    except TelegramBadRequest:
        await message.answer("❌ لا يمكنني طرد هذا العضو.")


@router.message(Command("mute"))
async def mute_user(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد كتمه.")
        return

    target = message.reply_to_message.from_user
    args = command.args or ""
    parts = args.split(maxsplit=1) if args else []

    duration_str = parts[0] if parts else None
    reason = parts[1] if len(parts) > 1 else "بدون سبب"

    until_date = None
    if duration_str:
        seconds = parse_duration(duration_str)
        if seconds:
            until_date = datetime.now(timezone.utc) + timedelta(seconds=seconds)

    permissions = ChatPermissions(can_send_messages=False)

    try:
        await bot.restrict_chat_member(
            message.chat.id, target.id, permissions, until_date=until_date
        )
        duration_text = f"لمدة {duration_str}" if duration_str else "بشكل دائم"
        await message.answer(
            f"🔇 **تم كتم العضو**\n\n"
            f"👤 الاسم: {target.full_name}\n"
            f"⏱️ {duration_text}\n"
            f"📝 السبب: {reason}"
        )
        await add_log(message.chat.id, message.from_user.id, f"mute {target.id}: {reason}")
    except TelegramBadRequest:
        await message.answer("❌ لا يمكنني كتم هذا العضو.")


@router.message(Command("unmute"))
async def unmute_user(message: Message):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد رفع كتمه.")
        return

    target = message.reply_to_message.from_user
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )

    try:
        await bot.restrict_chat_member(message.chat.id, target.id, permissions)
        await message.answer(f"✅ تم رفع الكتم عن {target.full_name}")
        await add_log(message.chat.id, message.from_user.id, f"unmute {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ تعذر رفع الكتم.")


@router.message(Command("warn"))
async def warn_user(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد تحذيره.")
        return

    target = message.reply_to_message.from_user
    reason = command.args or "بدون سبب"

    count = await add_warning(message.chat.id, target.id, reason)

    if count >= 3:
        permissions = ChatPermissions(can_send_messages=False)
        try:
            await bot.restrict_chat_member(message.chat.id, target.id, permissions)
            await clear_warnings(message.chat.id, target.id)
            await message.answer(
                f"⚠️ **تحذير {count}/3** — تم كتم {target.full_name} تلقائياً!\n"
                f"📝 السبب: {reason}"
            )
        except TelegramBadRequest:
            await message.answer(f"⚠️ وصل {target.full_name} إلى 3 تحذيرات لكن تعذر كتمه.")
    else:
        await message.answer(
            f"⚠️ **تحذير {count}/3**\n\n"
            f"👤 الاسم: {target.full_name}\n"
            f"📝 السبب: {reason}"
        )
    await add_log(message.chat.id, message.from_user.id, f"warn {target.id}: {reason}")


@router.message(Command("unwarn"))
async def unwarn_user(message: Message):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على رسالة العضو المراد إزالة تحذيراته.")
        return

    target = message.reply_to_message.from_user
    await clear_warnings(message.chat.id, target.id)
    await message.answer(f"✅ تم إزالة جميع تحذيرات {target.full_name}")


@router.message(Command("purge"))
async def purge_messages(message: Message):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على الرسالة التي تريد الحذف منها.")
        return

    try:
        msg_id = message.reply_to_message.message_id
        deleted = 0
        for i in range(msg_id, message.message_id + 1):
            try:
                await bot.delete_message(message.chat.id, i)
                deleted += 1
            except Exception:
                pass
        await message.answer(f"🧹 تم حذف {deleted} رسالة.")
    except Exception as e:
        await message.answer(f"❌ حدث خطأ: {e}")


@router.message(Command("pin"))
async def pin_message(message: Message):
    if not message.from_user.is_chat_admin():
        return

    if not message.reply_to_message:
        await message.reply("رد على الرسالة المراد تثبيتها.")
        return

    try:
        await bot.pin_chat_message(
            message.chat.id,
            message.reply_to_message.message_id,
            disable_notification=False
        )
        await message.answer("📌 تم تثبيت الرسالة.")
    except TelegramBadRequest:
        await message.answer("❌ تعذر تثبيت الرسالة.")

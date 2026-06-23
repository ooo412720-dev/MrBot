# app/handlers/group.py

from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot.bot import bot
from app.database.db import (
    get_or_create_group_settings, update_group_setting, add_log
)

router = Router()


@router.message(Command("rules"))
async def show_rules(message: Message):
    settings = await get_or_create_group_settings(message.chat.id)
    if settings.rules_text:
        await message.answer(f"📜 **قوانين الجروب:**\n\n{settings.rules_text}")
    else:
        await message.answer("ℹ️ لم يتم تعيين قوانين بعد. استخدم /setrules لتعيينها.")


@router.message(Command("setrules"))
async def set_rules(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    rules = command.args
    if not rules:
        await message.reply("اكتب القوانين بعد الأمر.\nمثال: /setrules 1. لا سبام\n2. لا إعلانات")
        return

    await update_group_setting(message.chat.id, "rules_text", rules)
    await message.answer("✅ تم تعيين قوانين الجروب.")
    await add_log(message.chat.id, message.from_user.id, "set_rules")


@router.message(Command("id"))
async def show_id(message: Message):
    user = message.from_user
    chat = message.chat
    text = (
        f"🆔 **معلومات**\n\n"
        f"👤 المستخدم: {user.full_name}\n"
        f"🆔 User ID: `{user.id}`\n"
        f"💬 Chat ID: `{chat.id}`\n"
        f"📛 النوع: {chat.type}\n"
    )
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        text += (
            f"\n📋 **معلومات المردود عليه:**\n"
            f"👤 الاسم: {target.full_name}\n"
            f"🆔 ID: `{target.id}`"
        )
    await message.answer(text)


@router.message(Command("info"))
async def user_info(message: Message):
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        target = message.from_user

    text = (
        f"👤 **معلومات المستخدم**\n\n"
        f"📛 الاسم: {target.full_name}\n"
        f"🆔 ID: `{target.id}`\n"
        f"👤 Username: @{target.username}\n" if target.username else
        f"👤 Username: لا يوجد\n"
    )
    await message.answer(text)


@router.message(Command("admins"))
async def list_admins(message: Message):
    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        admin_list = []
        for admin in admins:
            name = admin.user.full_name
            status = "👑 المالك" if admin.status == "creator" else "🔧 مشرف"
            admin_list.append(f"{status} — {name}")
        await message.answer(
            "📋 **قائمة المشرفين:**\n\n" + "\n".join(admin_list)
        )
    except Exception as e:
        await message.answer(f"❌ تعذر جلب قائمة المشرفين: {e}")


@router.message(Command("report"))
async def report_message(message: Message):
    if not message.reply_to_message:
        await message.reply("رد على الرسالة التي تريد الإبلاغ عنها.")
        return

    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        admin_mentions = []
        for admin in admins:
            if not admin.user.is_bot:
                admin_mentions.append(f"<a href='tg://user?id={admin.user.id}'>👤</a>")

        target = message.reply_to_message.from_user
        await message.answer(
            f"🚨 **تبليغ**\n\n"
            f"👤 المبلغ عنه: {target.full_name}\n"
            f"🆔 ID: `{target.id}`\n"
            f"📎 الرسالة: تم الإبلاغ عنها\n\n"
            f"{' '.join(admin_mentions[:5])}"
        )
    except Exception:
        await message.answer("❌ تعذر إرسال التبليغ.")


@router.message(Command("link"))
async def group_link(message: Message):
    try:
        chat = await bot.get_chat(message.chat.id)
        if chat.username:
            await message.answer(f"🔗 رابط الجروب: https://t.me/{chat.username}")
        elif chat.invite_link:
            await message.answer(f"🔗 رابط الدعوة: {chat.invite_link}")
        else:
            try:
                link = await bot.export_chat_invite_link(message.chat.id)
                await message.answer(f"🔗 رابط الدعوة: {link}")
            except Exception:
                await message.answer("ℹ️ تعذر الحصول على الرابط.")
    except Exception as e:
        await message.answer(f"❌ حدث خطأ: {e}")

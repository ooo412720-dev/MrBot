# app/handlers/welcome.py

import random

from aiogram import Router, Bot, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, ChatMemberUpdated, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.bot import bot
from app.database.db import (
    get_or_create_group_settings, update_group_setting,
    save_captcha, verify_captcha, get_or_create_user, add_log
)

router = Router()


@router.message(Command("setwelcome"))
async def set_welcome(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    text = command.args
    if not text:
        await message.reply(
            "اكتب رسالة الترحيب بعد الأمر.\n\n"
            "المتغيرات المتاحة:\n"
            "{name} — اسم العضو\n"
            "{chat} — اسم الجروب\n\n"
            "مثال: /setwelcome أهلاً {name} في {chat}!"
        )
        return

    await update_group_setting(message.chat.id, "welcome_text", text)
    await message.answer("✅ تم تعيين رسالة الترحيب.")


@router.message(Command("welcome"))
async def show_welcome(message: Message):
    settings = await get_or_create_group_settings(message.chat.id)
    if settings.welcome_text:
        formatted = settings.welcome_text.format(
            name=message.from_user.full_name,
            chat=message.chat.title or "الجروب"
        )
        await message.answer(f"👋 {formatted}")
    else:
        await message.answer("ℹ️ لم يتم تعيين رسالة ترحيب. استخدم /setwelcome")


@router.message(Command("captcha"))
async def toggle_captcha(message: Message):
    if not message.from_user.is_chat_admin():
        return

    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.captcha_enabled
    await update_group_setting(message.chat.id, "captcha_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"🤖 الكابتشا: {status}")


@router.message(Command("welcome_toggle"))
async def toggle_welcome(message: Message):
    if not message.from_user.is_chat_admin():
        return

    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.welcome_enabled
    await update_group_setting(message.chat.id, "welcome_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"👋 الترحيب: {status}")


@router.chat_member()
async def on_member_join(event: ChatMemberUpdated):
    if event.old_chat_member.status != "left" and event.old_chat_member.status != "kicked":
        return

    new_member = event.new_chat_member.user
    chat_id = event.chat.id

    if new_member.is_bot:
        return

    settings = await get_or_create_group_settings(chat_id, event.chat.title)

    if settings.welcome_enabled:
        welcome_text = settings.welcome_text or "👋 أهلاً {name} في {chat}!"
        try:
            formatted = welcome_text.format(
                name=new_member.full_name,
                chat=event.chat.title or "الجروب"
            )
            await bot.send_message(chat_id, formatted)
        except Exception:
            pass

    if settings.captcha_enabled:
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        answer = str(a + b)

        await save_captcha(new_member.id, chat_id, answer)

        permissions = ChatPermissions(can_send_messages=True)
        try:
            await bot.restrict_chat_member(chat_id, new_member.id, permissions)
        except Exception:
            pass

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{a} + {b} = ?", callback_data="captcha_none")],
            [
                InlineKeyboardButton(text=str(answer), callback_data=f"captcha:{new_member.id}:{answer}"),
                InlineKeyboardButton(text=str(answer + 1), callback_data=f"captcha:{new_member.id}:{answer+1}"),
                InlineKeyboardButton(text=str(answer - 1), callback_data=f"captcha:{new_member.id}:{answer-1}"),
            ]
        ])

        await bot.send_message(
            chat_id,
            f"🤖 {new_member.full_name}،\nأثبت أنك لست روبوت!\nحل العملية الحسابية:",
            reply_markup=kb
        )

    await get_or_create_user(new_member.id, new_member.username, new_member.full_name)
    await add_log(chat_id, new_member.id, "joined")


@router.callback_query(F.data.startswith("captcha:"))
async def captcha_callback(callback):
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer()
        return

    target_user_id = int(parts[1])
    selected_answer = parts[2]

    if callback.from_user.id != target_user_id:
        await callback.answer("هذا ليس لك!", show_alert=True)
        return

    chat_id = callback.message.chat.id
    is_correct = await verify_captcha(target_user_id, chat_id, selected_answer)

    if is_correct:
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
            await bot.restrict_chat_member(chat_id, target_user_id, permissions)
        except Exception:
            pass
        await callback.message.edit_text(f"✅ تم التحقق! أهلاً بك.")
        await callback.answer("تم بنجاح!")
    else:
        await callback.answer("❌ إجابة خاطئة!", show_alert=True)

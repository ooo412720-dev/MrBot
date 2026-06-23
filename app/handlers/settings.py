# app/handlers/settings.py

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.database.db import get_or_create_group_settings, update_group_setting

router = Router()


def build_settings_kb(settings) -> InlineKeyboardMarkup:
    def btn(label: str, enabled: bool, key: str) -> InlineKeyboardButton:
        icon = "✅" if enabled else "❌"
        return InlineKeyboardButton(
            text=f"{icon} {label}",
            callback_data=f"toggle:{key}"
        )

    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("الترحيب", settings.welcome_enabled, "welcome_enabled")],
        [btn("الكابتشا", settings.captcha_enabled, "captcha_enabled")],
        [btn("حظر الروابط", settings.antilink_enabled, "antilink_enabled")],
        [btn("مكافحة السبام", settings.antispam_enabled, "antispam_enabled")],
        [btn("قفل الوسائط", settings.lock_media, "lock_media")],
        [btn("قفل الملصقات", settings.lock_stickers, "lock_stickers")],
        [btn("قفل التوجيه", settings.lock_forward, "lock_forward")],
    ])


@router.message(Command("settings"))
async def show_settings(message: Message):
    if not message.from_user.is_chat_admin():
        return

    settings = await get_or_create_group_settings(message.chat.id)
    kb = build_settings_kb(settings)
    await message.answer(
        "⚙️ **إعدادات الجروب**\n\nاضغط على أي ميزة لتبديلها:",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("toggle:"))
async def toggle_setting(callback: CallbackQuery):
    if not callback.from_user.is_chat_admin():
        await callback.answer("للمشرفين فقط!", show_alert=True)
        return

    key = callback.data.split(":", 1)[1]
    settings = await get_or_create_group_settings(callback.message.chat.id)

    current = getattr(settings, key, False)
    new_val = not current
    await update_group_setting(callback.message.chat.id, key, new_val)

    settings = await get_or_create_group_settings(callback.message.chat.id)
    kb = build_settings_kb(settings)
    await callback.message.edit_reply_markup(reply_markup=kb)
    await callback.answer(f"{'✅' if new_val else '❌'} {key}")

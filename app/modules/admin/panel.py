# app/modules/admin/panel.py

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def admin_panel():
    keyboard = [
        [InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")],
        [InlineKeyboardButton("👥 الرتب", callback_data="roles")],
        [InlineKeyboardButton("📝 السجلات", callback_data="logs")],
        [InlineKeyboardButton("👁 الهمسات", callback_data="whispers")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

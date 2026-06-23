# app/modules/voting/service.py

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


def vote_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton("👍", callback_data="vote_yes"),
            InlineKeyboardButton("👎", callback_data="vote_no")
        ]
    ])

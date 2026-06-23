# app/handlers/notes.py

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.database.db import (
    save_note, get_note, get_notes, delete_note,
    add_filter, get_filters
)

router = Router()


@router.message(Command("save"))
async def save_note_handler(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    args = command.args
    if not args:
        await message.reply(
            "📝 الاستخدام: /save <name> <content>\n"
            "مثال: /save rules القوانين هنا"
        )
        return

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("⚠️ اكتب اسم الملاحظة ثم محتواها.")
        return

    name, content = parts
    await save_note(message.chat.id, name.lower(), content, message.from_user.id)
    await message.answer(f"💾 تم حفظ الملاحظة: {name}")


@router.message(Command("get"))
async def get_note_handler(message: Message, command: CommandObject):
    name = (command.args or "").lower().strip()
    if not name:
        await message.reply("⚠️ اكتب اسم الملاحظة.\nمثال: /get rules")
        return

    note = await get_note(message.chat.id, name)
    if note:
        await message.answer(f"📝 **{name}:**\n\n{note.content}")
    else:
        await message.answer(f"❌ لا توجد ملاحظة باسم: {name}")


@router.message(Command("notes"))
async def list_notes(message: Message):
    notes = await get_notes(message.chat.id)
    if not notes:
        await message.answer("ℹ️ لا توجد ملاحظات محفوظة.")
        return

    names = "\n".join(f"• {n.name}" for n in notes)
    await message.answer(f"📋 **الملاحظات المحفوظة:**\n\n{names}")


@router.message(Command("delete"))
async def delete_note_handler(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    name = (command.args or "").lower().strip()
    if not name:
        await message.reply("⚠️ اكتب اسم الملاحظة.\nمثال: /delete rules")
        return

    deleted = await delete_note(message.chat.id, name)
    if deleted:
        await message.answer(f"🗑️ تم حذف الملاحظة: {name}")
    else:
        await message.answer(f"❌ لا توجد ملاحظة باسم: {name}")


@router.message(Command("filter"))
async def add_filter_handler(message: Message, command: CommandObject):
    if not message.from_user.is_chat_admin():
        return

    args = command.args
    if not args:
        await message.reply(
            "📝 الاستخدام: /filter <word> <reply>\n"
            "مثال: /filter مرحباً أهلاً وسهلاً"
        )
        return

    parts = args.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("⚠️ اكتب الكلمة ثم الرد.")
        return

    word, reply = parts
    await add_filter(message.chat.id, word.lower(), reply)
    await message.answer(f"✅ تم إضافة فلتر: كلما يكتب أحد '{word}' سيرد البوت بـ: {reply}")


@router.message(F.text)
async def check_filters(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    filters = await get_filters(message.chat.id)
    if not filters:
        return

    text_lower = message.text.lower()
    for f in filters:
        if f.word.lower() in text_lower:
            await message.reply(f.reply)
            return

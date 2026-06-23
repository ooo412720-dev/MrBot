# app/handlers/commands.py

from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

from app.bot.bot import bot
from app.core.logger import logger
from app.database.db import get_all_groups

router = Router()

BOOT_IMAGE = Path(__file__).resolve().parent.parent.parent / "boot.jpg"


async def edit_message(message: Message, text: str, kb: InlineKeyboardMarkup):
    """يعدل الرسالة سواء كانت صورة أو نص"""
    try:
        if message.photo:
            await message.edit_caption(caption=text, reply_markup=kb)
        else:
            await message.edit_text(text=text, reply_markup=kb)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=kb)


@router.message(Command("start"))
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="➕ أضفني كمشرف في مجموعتك",
            callback_data="show_my_groups"
        )],
        [InlineKeyboardButton(
            text="📋 قائمة الأوامر",
            callback_data="show_help"
        )]
    ])

    if BOOT_IMAGE.exists():
        try:
            photo = FSInputFile(BOOT_IMAGE)
            await message.answer_photo(
                photo=photo,
                caption=(
                    "🤖 مرحباً بك في MrBot\n\n"
                    "أنا بوت إدارة المجموعات المتكامل.\n\n"
                    "أهم الميزات:\n"
                    "• إدارة الأعضاء (حظر/طرد/كتم/تحذير)\n"
                    "• حماية من السبام والروابط والغارات\n"
                    "• ترحيب تلقائي + كابتشا\n"
                    "• ملاحظات وفلاتر\n"
                    "• نظام نقاط ومستويات\n"
                    "• إعدادات قابلة للتخصيص\n\n"
                    "اضغط على الزر أدناه لإضافتي لمجموعتك."
                ),
                reply_markup=kb
            )
            return
        except Exception as e:
            logger.warning(f"Could not send photo: {e}")

    await message.answer(
        "🤖 مرحباً بك في MrBot\n\n"
        "أنا بوت إدارة المجموعات المتكامل.\n\n"
        "اضغط على الزر لإضافتي لمجموعتك.",
        reply_markup=kb
    )


@router.callback_query(F.data == "show_my_groups")
async def show_my_groups(callback: CallbackQuery):
    user_id = callback.from_user.id

    try:
        groups = await get_all_groups()
    except Exception as e:
        logger.error(f"Database error: {e}")
        await callback.answer("حدث خطأ في قاعدة البيانات. حاول لاحقاً.", show_alert=True)
        return

    if not groups:
        me = await bot.get_me()
        await callback.answer(
            f"لا توجد مجموعات مسجلة بعد!\n\n"
            f"أضفني لمجموعة عبر الرابط:\n"
            f"https://t.me/{me.username}?startgroup=true",
            show_alert=True
        )
        return

    admin_groups = []
    for g in groups:
        try:
            member = await bot.get_chat_member(g.group_id, user_id)
            if member.status in ("creator", "administrator"):
                title = g.title or f"ID: {g.group_id}"
                admin_groups.append((g.group_id, title))
        except Exception:
            continue

    if not admin_groups:
        me = await bot.get_me()
        await callback.answer(
            f"أنت لست مشرفاً في أي مجموعة.\n\n"
            f"أضفني لمجموعة جديدة:\n"
            f"https://t.me/{me.username}?startgroup=true",
            show_alert=True
        )
        return

    keyboard = []
    for group_id, title in admin_groups:
        keyboard.append([
            InlineKeyboardButton(
                text=f"💬 {title}",
                url=f"https://t.me/c/{str(group_id)[4:]}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="➕ مجموعة جديدة", callback_data="add_to_group"),
        InlineKeyboardButton(text="↩️ رجوع", callback_data="back_to_start")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)

    text = (
        "📋 مجموعاتك التي أدمن فيها:\n\n"
        + "\n".join(f"• {title}" for _, title in admin_groups)
        + "\n\nاضغط على أي مجموعة للفتحها."
    )

    await edit_message(callback.message, text, kb)
    await callback.answer()


@router.callback_query(F.data == "add_to_group")
async def add_to_group_callback(callback: CallbackQuery):
    me = await bot.get_me()
    await callback.answer(
        f"اضغط على هذا الرابط لإضافتي لمجموعتك:\n\n"
        f"https://t.me/{me.username}?startgroup=true",
        show_alert=True
    )


@router.callback_query(F.data == "show_help")
async def show_help_callback(callback: CallbackQuery):
    help_text = (
        "📋 قائمة الأوامر\n\n"
        "الأوامر الإدارية:\n"
        "• /ban — حظر عضو (بالرد)\n"
        "• /unban — رفع الحظر\n"
        "• /kick — طرد عضو\n"
        "• /mute — كتم عضو (بالرد)\n"
        "• /unmute — رفع الكتم\n"
        "• /warn — تحذير عضو\n"
        "• /unwarn — إزالة التحذيرات\n"
        "• /purge — حذف رسائل (بالرد)\n"
        "• /pin — تثبيت رسالة (بالرد)\n\n"
        "أوامر المجموعة:\n"
        "• /rules — عرض القوانين\n"
        "• /setrules — تعيين القوانين\n"
        "• /id — معلومات الحساب\n"
        "• /info — معلومات مستخدم (بالرد)\n"
        "• /admins — قائمة المشرفين\n"
        "• /report — تبليغ عن رسالة\n\n"
        "الترحيب والحماية:\n"
        "• /setwelcome — تعيين ترحيب\n"
        "• /captcha — تفعيل الكابتشا\n"
        "• /antilink — حظر الروابط\n"
        "• /lock — قفل نوع رسائل\n"
        "• /unlock — فتح نوع رسائل\n\n"
        "الملاحظات:\n"
        "• /save <name> <text> — حفظ ملاحظة\n"
        "• /get <name> — عرض ملاحظة\n"
        "• /notes — قائمة الملاحظات\n"
        "• /delete <name> — حذف ملاحظة\n"
        "• /filter <word> <reply> — فلتر تلقائي\n\n"
        "النقاط والسمعة:\n"
        "• /rank — مستواك\n"
        "• /top — الأكثر نشاطاً\n"
        "• /rep — إعطاء سمعة (بالرد)\n\n"
        "الإعدادات:\n"
        "• /settings — لوحة الإعدادات\n"
        "• /whisper — همسة خاصة (بالرد)\n"
    )
    await callback.message.answer(help_text)
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="➕ أضفني كمشرف في مجموعتك",
            callback_data="show_my_groups"
        )],
        [InlineKeyboardButton(
            text="📋 قائمة الأوامر",
            callback_data="show_help"
        )]
    ])
    text = (
        "🤖 مرحباً بك في MrBot\n\n"
        "أنا بوت إدارة المجموعات المتكامل.\n\n"
        "اضغط على الزر أدناه لإضافتي لمجموعتك."
    )
    await edit_message(callback.message, text, kb)
    await callback.answer()


@router.message(Command("ping"))
async def ping_handler(message: Message):
    await message.answer("🏓 pong")


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "📋 قائمة الأوامر\n\n"
        "الأوامر الإدارية:\n"
        "• /ban — حظر عضو (بالرد)\n"
        "• /unban — رفع الحظر\n"
        "• /kick — طرد عضو\n"
        "• /mute — كتم عضو (بالرد)\n"
        "• /unmute — رفع الكتم\n"
        "• /warn — تحذير عضو\n"
        "• /unwarn — إزالة التحذيرات\n"
        "• /purge — حذف رسائل (بالرد)\n"
        "• /pin — تثبيت رسالة (بالرد)\n\n"
        "أوامر المجموعة:\n"
        "• /rules — عرض القوانين\n"
        "• /setrules — تعيين القوانين\n"
        "• /id — معلومات الحساب\n"
        "• /info — معلومات مستخدم (بالرد)\n"
        "• /admins — قائمة المشرفين\n"
        "• /report — تبليغ عن رسالة\n\n"
        "الترحيب والحماية:\n"
        "• /setwelcome — تعيين ترحيب\n"
        "• /captcha — تفعيل الكابتشا\n"
        "• /antilink — حظر الروابط\n"
        "• /lock — قفل نوع رسائل\n"
        "• /unlock — فتح نوع رسائل\n\n"
        "الملاحظات:\n"
        "• /save <name> <text> — حفظ ملاحظة\n"
        "• /get <name> — عرض ملاحظة\n"
        "• /notes — قائمة الملاحظات\n"
        "• /delete <name> — حذف ملاحظة\n"
        "• /filter <word> <reply> — فلتر تلقائي\n\n"
        "النقاط والسمعة:\n"
        "• /rank — مستواك\n"
        "• /top — الأكثر نشاطاً\n"
        "• /rep — إعطاء سمعة (بالرد)\n\n"
        "الإعدادات:\n"
        "• /settings — لوحة الإعدادات\n"
        "• /whisper — همسة خاصة (بالرد)\n"
    )
    await message.answer(help_text)

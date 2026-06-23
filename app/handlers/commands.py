# app/handlers/commands.py

from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest

from app.bot.bot import bot
from app.core.logger import logger
from app.database.db import get_all_groups, get_or_create_group_settings, get_or_create_user

router = Router()

BOOT_IMAGE = Path(__file__).resolve().parent.parent.parent / "boot.jpg"


async def edit_message(message: Message, text: str, kb: InlineKeyboardMarkup):
    try:
        if message.photo:
            await message.edit_caption(caption=text, reply_markup=kb)
        else:
            await message.edit_text(text=text, reply_markup=kb)
    except TelegramBadRequest:
        await message.answer(text, reply_markup=kb)


@router.message(Command("start"))
async def start_handler(message: Message):
    # تسجيل المستخدم
    await get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name
    )

    # تسجيل الجروب تلقائياً إذا كان /start داخل جروب
    if message.chat.type in ("group", "supergroup"):
        await get_or_create_group_settings(message.chat.id, message.chat.title)
        await message.answer(
            f"✅ تم تسجيل الجروب: {message.chat.title}\n"
            f"أرسل /help لعرض الأوامر."
        )
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="➕ أضفني لمجموعة",
            url=f"https://t.me/{(await bot.get_me()).username}?startgroup=true"
        )],
        [InlineKeyboardButton(
            text="📂 مجموعاتي",
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
                    "اضغط على زر (أضفني لمجموعة) للبدء."
                ),
                reply_markup=kb
            )
            return
        except Exception as e:
            logger.warning(f"Could not send photo: {e}")

    await message.answer(
        "🤖 مرحباً بك في MrBot\n\n"
        "اضغط على زر (أضفني لمجموعة) للبدء.",
        reply_markup=kb
    )


@router.callback_query(F.data == "show_my_groups")
async def show_my_groups(callback: CallbackQuery):
    user_id = callback.from_user.id
    me = await bot.get_me()
    add_link = f"https://t.me/{me.username}?startgroup=true"

    try:
        groups = await get_all_groups()
    except Exception as e:
        logger.error(f"Database error: {e}")
        groups = []

    admin_groups = []
    for g in groups:
        try:
            member = await bot.get_chat_member(g.group_id, user_id)
            if member.status in ("creator", "administrator"):
                title = g.title or f"ID: {g.group_id}"
                admin_groups.append((g.group_id, title))
        except Exception:
            continue

    keyboard = []

    # زر إضافة لمجموعة جديدة دائماً موجود
    keyboard.append([
        InlineKeyboardButton(text="➕ أضفني لمجموعة جديدة", url=add_link)
    ])

    # أزرار المجموعات الموجودة
    for group_id, title in admin_groups:
        group_str = str(group_id)
        if group_str.startswith("-100"):
            link = f"https://t.me/c/{group_str[4:]}"
        else:
            link = add_link
        keyboard.append([
            InlineKeyboardButton(text=f"💬 {title}", url=link)
        ])

    keyboard.append([
        InlineKeyboardButton(text="↩️ رجوع", callback_data="back_to_start")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if admin_groups:
        text = (
            "📋 مجموعاتك التي أدمن فيها:\n\n"
            + "\n".join(f"• {title}" for _, title in admin_groups)
            + "\n\nاضغط على أي مجموعة للفتحها أو أضف مجموعة جديدة."
        )
    else:
        text = (
            "📋 لا توجد مجموعات مسجلة بعد.\n\n"
            "اضغط على زر (أضفني لمجموعة جديدة) بالأعلى\n"
            "لإضافتي لمجموعتك كمشرف.\n\n"
            "بعد إضافتي أرسل /start داخل المجموعة لتسجيلها."
        )

    await edit_message(callback.message, text, kb)
    await callback.answer()


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
    me = await bot.get_me()
    add_link = f"https://t.me/{me.username}?startgroup=true"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ أضفني لمجموعة", url=add_link)],
        [InlineKeyboardButton(text="📂 مجموعاتي", callback_data="show_my_groups")],
        [InlineKeyboardButton(text="📋 قائمة الأوامر", callback_data="show_help")]
    ])
    text = (
        "🤖 مرحباً بك في MrBot\n\n"
        "أنا بوت إدارة المجموعات المتكامل.\n\n"
        "اضغط على زر (أضفني لمجموعة) للبدء."
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

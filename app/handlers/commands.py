# app/handlers/commands.py

from pathlib import Path

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.bot import bot
from app.database.db import get_all_groups

router = Router()

BOOT_IMAGE = Path(__file__).resolve().parent.parent.parent / "boot.jpg"


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
        photo = FSInputFile(BOOT_IMAGE)
        await message.answer_photo(
            photo=photo,
            caption=(
                "🤖 **مرحباً بك في MrBot**\n\n"
                "أنا بوت إدارة المجموعات المتكامل.\n\n"
                "**أهم الميزات:**\n"
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
    else:
        await message.answer(
            "🤖 **مرحباً بك في MrBot**\n\nاضغط على الزر لإضافتي لمجموعتك.",
            reply_markup=kb
        )


@router.callback_query(F.data == "show_my_groups")
async def show_my_groups(callback: CallbackQuery):
    user_id = callback.from_user.id
    groups = await get_all_groups()

    if not groups:
        await callback.answer("لا توجد مجموعات مسجلة بعد. أضفني لمجموعة وأرسل /start!", show_alert=True)
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
        await callback.answer("أنت لست مشرفاً في أي مجموعة يستخدمها البوت.", show_alert=True)
        return

    keyboard = []
    for group_id, title in admin_groups:
        keyboard.append([
            InlineKeyboardButton(
                text=f"💬 {title}",
                url=f"tg://openmessage?chat_id={group_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text="➕ مجموعة جديدة", callback_data="add_to_group"),
        InlineKeyboardButton(text="↩️ رجوع", callback_data="back_to_start")
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await callback.message.edit_caption(
        caption=(
            f"📋 **مجموعاتك التي أدمن فيها:**\n\n"
            + "\n".join(f"• {title}" for _, title in admin_groups)
            + "\n\nاضغط على أي مجموعة للفتحها."
        ),
        reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data == "add_to_group")
async def add_to_group_callback(callback: CallbackQuery):
    me = await bot.get_me()
    await callback.answer(
        f"اضغط على هذا الرابط لإضافتي لمجموعتك:\nhttps://t.me/{me.username}?startgroup=true",
        show_alert=True
    )


@router.callback_query(F.data == "show_help")
async def show_help_callback(callback: CallbackQuery):
    help_text = (
        "📋 **قائمة الأوامر**\n\n"
        "**الأوامر الإدارية:**\n"
        "• /ban — حظر عضو (بالرد)\n"
        "• /unban — رفع الحظر\n"
        "• /kick — طرد عضو\n"
        "• /mute — كتم عضو (بالرد)\n"
        "• /unmute — رفع الكتم\n"
        "• /warn — تحذير عضو\n"
        "• /unwarn — إزالة التحذيرات\n"
        "• /purge — حذف رسائل (بالرد)\n"
        "• /pin — تثبيت رسالة (بالرد)\n\n"
        "**أوامر المجموعة:**\n"
        "• /rules — عرض القوانين\n"
        "• /setrules — تعيين القوانين\n"
        "• /id — معلومات الحساب\n"
        "• /info — معلومات مستخدم (بالرد)\n"
        "• /admins — قائمة المشرفين\n"
        "• /report — تبليغ عن رسالة\n\n"
        "**الترحيب والحماية:**\n"
        "• /setwelcome — تعيين ترحيب\n"
        "• /captcha — تفعيل الكابتشا\n"
        "• /antilink — حظر الروابط\n"
        "• /lock — قفل نوع رسائل\n"
        "• /unlock — فتح نوع رسائل\n\n"
        "**الملاحظات:**\n"
        "• /save <name> <text> — حفظ ملاحظة\n"
        "• /get <name> — عرض ملاحظة\n"
        "• /notes — قائمة الملاحظات\n"
        "• /delete <name> — حذف ملاحظة\n"
        "• /filter <word> <reply> — فلتر تلقائي\n\n"
        "**النقاط والسمعة:**\n"
        "• /rank — مستواك\n"
        "• /top — الأكثر نشاطاً\n"
        "• /rep — إعطاء سمعة (بالرد)\n\n"
        "**الإعدادات:**\n"
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
    await callback.message.edit_caption(
        caption=(
            "🤖 **مرحباً بك في MrBot**\n\n"
            "أنا بوت إدارة المجموعات المتكامل.\n\n"
            "اضغط على الزر أدناه لإضافتي لمجموعتك."
        ),
        reply_markup=kb
    )
    await callback.answer()


@router.message(Command("ping"))
async def ping_handler(message: Message):
    await message.answer("🏓 pong")


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "📋 **قائمة الأوامر**\n\n"
        "**الأوامر الإدارية:**\n"
        "• /ban — حظر عضو (بالرد)\n"
        "• /unban — رفع الحظر\n"
        "• /kick — طرد عضو\n"
        "• /mute — كتم عضو (بالرد)\n"
        "• /unmute — رفع الكتم\n"
        "• /warn — تحذير عضو\n"
        "• /unwarn — إزالة التحذيرات\n"
        "• /purge — حذف رسائل (بالرد)\n"
        "• /pin — تثبيت رسالة (بالرد)\n\n"
        "**أوامر المجموعة:**\n"
        "• /rules — عرض القوانين\n"
        "• /setrules — تعيين القوانين\n"
        "• /id — معلومات الحساب\n"
        "• /info — معلومات مستخدم (بالرد)\n"
        "• /admins — قائمة المشرفين\n"
        "• /report — تبليغ عن رسالة\n\n"
        "**الترحيب والحماية:**\n"
        "• /setwelcome — تعيين ترحيب\n"
        "• /captcha — تفعيل الكابتشا\n"
        "• /antilink — حظر الروابط\n"
        "• /lock — قفل نوع رسائل\n"
        "• /unlock — فتح نوع رسائل\n\n"
        "**الملاحظات:**\n"
        "• /save <name> <text> — حفظ ملاحظة\n"
        "• /get <name> — عرض ملاحظة\n"
        "• /notes — قائمة الملاحظات\n"
        "• /delete <name> — حذف ملاحظة\n"
        "• /filter <word> <reply> — فلتر تلقائي\n\n"
        "**النقاط والسمعة:**\n"
        "• /rank — مستواك\n"
        "• /top — الأكثر نشاطاً\n"
        "• /rep — إعطاء سمعة (بالرد)\n\n"
        "**الإعدادات:**\n"
        "• /settings — لوحة الإعدادات\n"
        "• /whisper — همسة خاصة (بالرد)\n"
    )
    await message.answer(help_text)
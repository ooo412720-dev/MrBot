# app/handlers/arabic_commands.py
# أمر باللغة العربية وبدائل متعددة - بدون Markdown

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from app.bot.bot import bot
from app.core.logger import logger
from app.database.db import add_log

router = Router()

# ============================================================================
# ديكوريتور مخصص لدعم أمر واحد بعدة أسماء
# ============================================================================

def multi_command(*names):
    """ديكوريتور لدعم أمر واحد بعدة أسماء (عربي + إنجليزي)"""
    def decorator(handler):
        for name in names:
            router.message(Command(name))(handler)
        return handler
    return decorator


# ============================================================================
# أوامر الإدارة - الحظر والطرد والكتم
# ============================================================================

@multi_command("ban", "حظر", "طرد_نهائي", "block")
async def ban_user_arabic(message: Message):
    """حظر عضو من الجروب"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد حظره.
مثال: /حظر (بالرد)", parse_mode=None)
        return

    target = message.reply_to_message.from_user

    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await message.answer(
            f"🚫 تم حظر العضو

"
            f"👤 الاسم: {target.full_name}
"
            f"🆔 ID: {target.id}",
            parse_mode=None
        )
        await add_log(message.chat.id, message.from_user.id, f"ban {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ لا يمكنني حظر هذا العضو. تأكد من أنني مشرف.", parse_mode=None)


@multi_command("unban", "فك_الحظر", "رفع_الحظر", "unblock")
async def unban_user_arabic(message: Message):
    """رفع الحظر عن عضو"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد رفع حظره.", parse_mode=None)
        return

    target = message.reply_to_message.from_user

    try:
        await bot.unban_chat_member(message.chat.id, target.id, only_if_banned=True)
        await message.answer(f"✅ تم رفع الحظر عن {target.full_name}", parse_mode=None)
        await add_log(message.chat.id, message.from_user.id, f"unban {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ تعذر رفع الحظر.", parse_mode=None)


@multi_command("kick", "طرد", "اخراج", "remove")
async def kick_user_arabic(message: Message):
    """طرد عضو من الجروب"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد طرده.", parse_mode=None)
        return

    target = message.reply_to_message.from_user

    try:
        await bot.ban_chat_member(message.chat.id, target.id)
        await bot.unban_chat_member(message.chat.id, target.id, only_if_banned=True)
        await message.answer(
            f"👢 تم طرد العضو

"
            f"👤 الاسم: {target.full_name}",
            parse_mode=None
        )
        await add_log(message.chat.id, message.from_user.id, f"kick {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ لا يمكنني طرد هذا العضو.", parse_mode=None)


@multi_command("mute", "كتم", "سكوت", "silence")
async def mute_user_arabic(message: Message):
    """كتم عضو في الجروب"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply(
            "📌 رد على رسالة العضو المراد كتمه.
"
            "مثال: /كتم 1h (بالرد)",
            parse_mode=None
        )
        return

    target = message.reply_to_message.from_user

    from datetime import datetime, timedelta, timezone
    from aiogram.types import ChatPermissions

    args = message.text.split(maxsplit=1)
    duration_str = args[1] if len(args) > 1 else None

    until_date = None
    if duration_str:
        text = duration_str.lower().strip()
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400, "س": 1, "د": 60, "سا": 3600, "ي": 86400}
        for unit, multiplier in units.items():
            if text.endswith(unit):
                try:
                    num = int(text[:-1])
                    until_date = datetime.now(timezone.utc) + timedelta(seconds=num * multiplier)
                    break
                except ValueError:
                    pass

    permissions = ChatPermissions(can_send_messages=False)

    try:
        await bot.restrict_chat_member(message.chat.id, target.id, permissions, until_date=until_date)
        duration_text = f"لمدة {duration_str}" if duration_str else "بشكل دائم"
        await message.answer(
            f"🔇 تم كتم العضو

"
            f"👤 الاسم: {target.full_name}
"
            f"⏱️ {duration_text}",
            parse_mode=None
        )
        await add_log(message.chat.id, message.from_user.id, f"mute {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ لا يمكنني كتم هذا العضو.", parse_mode=None)


@multi_command("unmute", "فك_الكتم", "رفع_الكتم", "unsilence")
async def unmute_user_arabic(message: Message):
    """رفع الكتم عن عضو"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد رفع كتمه.", parse_mode=None)
        return

    target = message.reply_to_message.from_user
    from aiogram.types import ChatPermissions

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
        await message.answer(f"✅ تم رفع الكتم عن {target.full_name}", parse_mode=None)
        await add_log(message.chat.id, message.from_user.id, f"unmute {target.id}")
    except TelegramBadRequest:
        await message.answer("❌ تعذر رفع الكتم.", parse_mode=None)


@multi_command("warn", "تحذير", "انذار", "warning")
async def warn_user_arabic(message: Message):
    """إعطاء تحذير لعضو"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد تحذيره.", parse_mode=None)
        return

    target = message.reply_to_message.from_user
    args = message.text.split(maxsplit=1)
    reason = args[1] if len(args) > 1 else "بدون سبب"

    from app.database.db import add_warning, clear_warnings
    from aiogram.types import ChatPermissions

    count = await add_warning(message.chat.id, target.id, reason)

    if count >= 3:
        permissions = ChatPermissions(can_send_messages=False)
        try:
            await bot.restrict_chat_member(message.chat.id, target.id, permissions)
            await clear_warnings(message.chat.id, target.id)
            await message.answer(
                f"⚠️ تحذير {count}/3 — تم كتم {target.full_name} تلقائياً!
"
                f"📝 السبب: {reason}",
                parse_mode=None
            )
        except TelegramBadRequest:
            await message.answer(f"⚠️ وصل {target.full_name} إلى 3 تحذيرات لكن تعذر كتمه.", parse_mode=None)
    else:
        await message.answer(
            f"⚠️ تحذير {count}/3

"
            f"👤 الاسم: {target.full_name}
"
            f"📝 السبب: {reason}",
            parse_mode=None
        )
    await add_log(message.chat.id, message.from_user.id, f"warn {target.id}: {reason}")


@multi_command("unwarn", "حذف_التحذير", "مسح_التحذير", "clearwarn")
async def unwarn_user_arabic(message: Message):
    """مسح تحذيرات عضو"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد مسح تحذيراته.", parse_mode=None)
        return

    target = message.reply_to_message.from_user
    from app.database.db import clear_warnings

    await clear_warnings(message.chat.id, target.id)
    await message.answer(f"✅ تم مسح جميع تحذيرات {target.full_name}", parse_mode=None)


@multi_command("purge", "مسح", "حذف", "delete")
async def purge_messages_arabic(message: Message):
    """حذف رسائل"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على الرسالة التي تريد الحذف منها.", parse_mode=None)
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
        await message.answer(f"🧹 تم حذف {deleted} رسالة.", parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ حدث خطأ: {e}", parse_mode=None)


@multi_command("pin", "تثبيت", "fix")
async def pin_message_arabic(message: Message):
    """تثبيت رسالة"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    if not message.reply_to_message:
        await message.reply("📌 رد على الرسالة المراد تثبيتها.", parse_mode=None)
        return

    try:
        await bot.pin_chat_message(
            message.chat.id,
            message.reply_to_message.message_id,
            disable_notification=False
        )
        await message.answer("📌 تم تثبيت الرسالة.", parse_mode=None)
    except TelegramBadRequest:
        await message.answer("❌ تعذر تثبيت الرسالة.", parse_mode=None)


# ============================================================================
# أوامر المجموعة
# ============================================================================

@multi_command("rules", "قوانين", "قانون", "law")
async def show_rules_arabic(message: Message):
    """عرض قوانين الجروب"""
    from app.database.db import get_or_create_group_settings
    settings = await get_or_create_group_settings(message.chat.id)
    if settings.rules_text:
        await message.answer(f"📜 قوانين الجروب:

{settings.rules_text}", parse_mode=None)
    else:
        await message.answer("ℹ️ لم يتم تعيين قوانين بعد. استخدم /setrules أو /تعيين_قوانين", parse_mode=None)


@multi_command("setrules", "تعيين_قوانين", "قوانين_جديدة", "setlaw")
async def set_rules_arabic(message: Message):
    """تعيين قوانين الجروب"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    args = message.text.split(maxsplit=1)
    rules = args[1] if len(args) > 1 else None

    if not rules:
        await message.reply(
            "📝 اكتب القوانين بعد الأمر.
"
            "مثال: /تعيين_قوانين 1. لا سبام
2. لا إعلانات",
            parse_mode=None
        )
        return

    from app.database.db import update_group_setting
    await update_group_setting(message.chat.id, "rules_text", rules)
    await message.answer("✅ تم تعيين قوانين الجروب.", parse_mode=None)
    await add_log(message.chat.id, message.from_user.id, "set_rules")


@multi_command("id", "ايدي", "هوية", "identity")
async def show_id_arabic(message: Message):
    """عرض معلومات الحساب"""
    user = message.from_user
    chat = message.chat
    text = (
        f"🆔 معلومات

"
        f"👤 المستخدم: {user.full_name}
"
        f"🆔 User ID: {user.id}
"
        f"💬 Chat ID: {chat.id}
"
        f"📛 النوع: {chat.type}
"
    )
    if message.reply_to_message:
        target = message.reply_to_message.from_user
        text += (
            f"
📋 معلومات المردود عليه:
"
            f"👤 الاسم: {target.full_name}
"
            f"🆔 ID: {target.id}"
        )
    await message.answer(text, parse_mode=None)


@multi_command("info", "معلومات", "بيانات", "data")
async def user_info_arabic(message: Message):
    """معلومات مستخدم"""
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        target = message.from_user

    text = (
        f"👤 معلومات المستخدم

"
        f"📛 الاسم: {target.full_name}
"
        f"🆔 ID: {target.id}
"
    )
    if target.username:
        text += f"👤 Username: @{target.username}
"
    else:
        text += f"👤 Username: لا يوجد
"
    await message.answer(text, parse_mode=None)


@multi_command("admins", "المشرفين", "ادمن", "adminlist")
async def list_admins_arabic(message: Message):
    """قائمة المشرفين"""
    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        admin_list = []
        for admin in admins:
            name = admin.user.full_name
            status = "👑 المالك" if admin.status == "creator" else "🔧 مشرف"
            admin_list.append(f"{status} — {name}")
        await message.answer(
            "📋 قائمة المشرفين:

" + "
".join(admin_list),
            parse_mode=None
        )
    except Exception as e:
        await message.answer(f"❌ تعذر جلب قائمة المشرفين: {e}", parse_mode=None)


@multi_command("report", "تبليغ", "بلاغ", "reportuser")
async def report_message_arabic(message: Message):
    """تبليغ عن رسالة"""
    if not message.reply_to_message:
        await message.reply("📌 رد على الرسالة التي تريد الإبلاغ عنها.", parse_mode=None)
        return

    try:
        admins = await bot.get_chat_administrators(message.chat.id)
        admin_mentions = []
        for admin in admins:
            if not admin.user.is_bot:
                admin_mentions.append(f"@{admin.user.username}" if admin.user.username else admin.user.full_name)

        target = message.reply_to_message.from_user
        await message.answer(
            f"🚨 تبليغ

"
            f"👤 المبلغ عنه: {target.full_name}
"
            f"🆔 ID: {target.id}

"
            f"{' '.join(admin_mentions[:5])}",
            parse_mode=None
        )
    except Exception:
        await message.answer("❌ تعذر إرسال التبليغ.", parse_mode=None)


@multi_command("link", "رابط", "لينك", "url")
async def group_link_arabic(message: Message):
    """رابط الجروب"""
    try:
        chat = await bot.get_chat(message.chat.id)
        if chat.username:
            await message.answer(f"🔗 رابط الجروب: https://t.me/{chat.username}", parse_mode=None)
        elif chat.invite_link:
            await message.answer(f"🔗 رابط الدعوة: {chat.invite_link}", parse_mode=None)
        else:
            try:
                link = await bot.export_chat_invite_link(message.chat.id)
                await message.answer(f"🔗 رابط الدعوة: {link}", parse_mode=None)
            except Exception:
                await message.answer("ℹ️ تعذر الحصول على الرابط.", parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ حدث خطأ: {e}", parse_mode=None)


# ============================================================================
# الترحيب والحماية
# ============================================================================

@multi_command("setwelcome", "تعيين_ترحيب", "ترحيب", "welcome_msg")
async def set_welcome_arabic(message: Message):
    """تعيين رسالة ترحيب"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    args = message.text.split(maxsplit=1)
    text = args[1] if len(args) > 1 else None

    if not text:
        await message.reply(
            "📝 اكتب رسالة الترحيب بعد الأمر.

"
            "المتغيرات المتاحة:
"
            "{name} — اسم العضو
"
            "{chat} — اسم الجروب

"
            "مثال: /ترحيب أهلاً {name} في {chat}!",
            parse_mode=None
        )
        return

    from app.database.db import update_group_setting
    await update_group_setting(message.chat.id, "welcome_text", text)
    await message.answer("✅ تم تعيين رسالة الترحيب.", parse_mode=None)


@multi_command("welcome", "عرض_ترحيب", "الترحيب", "showwelcome")
async def show_welcome_arabic(message: Message):
    """عرض رسالة الترحيب"""
    from app.database.db import get_or_create_group_settings
    settings = await get_or_create_group_settings(message.chat.id)
    if settings.welcome_text:
        formatted = settings.welcome_text.format(
            name=message.from_user.full_name,
            chat=message.chat.title or "الجروب"
        )
        await message.answer(f"👋 {formatted}", parse_mode=None)
    else:
        await message.answer("ℹ️ لم يتم تعيين رسالة ترحيب. استخدم /setwelcome أو /تعيين_ترحيب", parse_mode=None)


@multi_command("captcha", "كابتشا", "تحقق", "verify")
async def toggle_captcha_arabic(message: Message):
    """تفعيل/إيقاف الكابتشا"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    from app.database.db import get_or_create_group_settings, update_group_setting
    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.captcha_enabled
    await update_group_setting(message.chat.id, "captcha_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"🤖 الكابتشا: {status}", parse_mode=None)


@multi_command("antilink", "حظر_روابط", "لینك", "nolink")
async def toggle_antilink_arabic(message: Message):
    """تفعيل/إيقاف حظر الروابط"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    from app.database.db import get_or_create_group_settings, update_group_setting
    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.antilink_enabled
    await update_group_setting(message.chat.id, "antilink_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"🔗 حظر الروابط: {status}", parse_mode=None)


@multi_command("antispam", "مكافحة_سبام", "سبام", "nospam")
async def toggle_antispam_arabic(message: Message):
    """تفعيل/إيقاف مكافحة السبام"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    from app.database.db import get_or_create_group_settings, update_group_setting
    settings = await get_or_create_group_settings(message.chat.id)
    new_val = not settings.antispam_enabled
    await update_group_setting(message.chat.id, "antispam_enabled", new_val)
    status = "✅ مفعّل" if new_val else "❌ معطل"
    await message.answer(f"🛡️ مكافحة السبام: {status}", parse_mode=None)


@multi_command("lock", "قفل", "اغلاق", "close")
async def lock_media_arabic(message: Message):
    """قفل وسائط"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    args = message.text.split(maxsplit=1)
    lock_type = args[1].lower().strip() if len(args) > 1 else ""

    from app.database.db import get_or_create_group_settings, update_group_setting

    if lock_type in ("media", "photos", "صور", "وسائط"):
        await update_group_setting(message.chat.id, "lock_media", True)
        await message.answer("🔒 تم قفل الصور والوسائط.", parse_mode=None)
    elif lock_type in ("stickers", "ملصقات", "ستيكر"):
        await update_group_setting(message.chat.id, "lock_stickers", True)
        await message.answer("🔒 تم قفل الملصقات.", parse_mode=None)
    elif lock_type in ("forward", "توجيه", "اعادة"):
        await update_group_setting(message.chat.id, "lock_forward", True)
        await message.answer("🔒 تم قفل التوجيه.", parse_mode=None)
    elif lock_type in ("all", "الكل", "كل"):
        await update_group_setting(message.chat.id, "lock_media", True)
        await update_group_setting(message.chat.id, "lock_stickers", True)
        await update_group_setting(message.chat.id, "lock_forward", True)
        await message.answer("🔒 تم قفل كل الوسائط.", parse_mode=None)
    else:
        await message.reply(
            "📝 الاستخدام: /قفل <نوع>

"
            "الأنواع: media, stickers, forward, all
"
            "أو: صور, ملصقات, توجيه, كل",
            parse_mode=None
        )


@multi_command("unlock", "فتح", "افتح", "open")
async def unlock_media_arabic(message: Message):
    """فتح وسائط"""
    if not message.from_user.is_chat_admin():
        await message.reply("❌ هذا الأمر للمشرفين فقط!", parse_mode=None)
        return

    args = message.text.split(maxsplit=1)
    lock_type = args[1].lower().strip() if len(args) > 1 else ""

    from app.database.db import get_or_create_group_settings, update_group_setting

    if lock_type in ("media", "photos", "صور", "وسائط"):
        await update_group_setting(message.chat.id, "lock_media", False)
        await message.answer("🔓 تم فتح الصور والوسائط.", parse_mode=None)
    elif lock_type in ("stickers", "ملصقات", "ستيكر"):
        await update_group_setting(message.chat.id, "lock_stickers", False)
        await message.answer("🔓 تم فتح الملصقات.", parse_mode=None)
    elif lock_type in ("forward", "توجيه", "اعادة"):
        await update_group_setting(message.chat.id, "lock_forward", False)
        await message.answer("🔓 تم فتح التوجيه.", parse_mode=None)
    elif lock_type in ("all", "الكل", "كل"):
        await update_group_setting(message.chat.id, "lock_media", False)
        await update_group_setting(message.chat.id, "lock_stickers", False)
        await update_group_setting(message.chat.id, "lock_forward", False)
        await message.answer("🔓 تم فتح كل الوسائط.", parse_mode=None)
    else:
        await message.reply(
            "📝 الاستخدام: /فتح <نوع>

"
            "الأنواع: media, stickers, forward, all
"
            "أو: صور, ملصقات, توجيه, كل",
            parse_mode=None
        )


# ============================================================================
# الملاحظات والفلاتر
# ============================================================================

@multi_command("save", "حفظ", "احفظ", "addnote")
async def save_note_arabic(message: Message):
    """حفظ ملاحظة"""
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply(
            "📝 الاستخدام: /حفظ <اسم> <نص>
"
            "مثال: /حفظ rules لا سبام في الجروب",
            parse_mode=None
        )
        return

    name = args[1]
    content = args[2]
    from app.database.db import save_note
    await save_note(message.chat.id, name, content, message.from_user.id)
    await message.answer(f"✅ تم حفظ الملاحظة: {name}", parse_mode=None)


@multi_command("get", "جلب", "عرض", "shownote")
async def get_note_arabic(message: Message):
    """عرض ملاحظة"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("📝 الاستخدام: /جلب <اسم>
مثال: /جلب rules", parse_mode=None)
        return

    name = args[1]
    from app.database.db import get_note
    note = await get_note(message.chat.id, name)
    if note:
        await message.answer(note.content, parse_mode=None)
    else:
        await message.answer(f"❌ الملاحظة {name} غير موجودة.", parse_mode=None)


@multi_command("notes", "ملاحظات", "قائمة", "listnotes")
async def list_notes_arabic(message: Message):
    """قائمة الملاحظات"""
    from app.database.db import get_notes
    notes = await get_notes(message.chat.id)
    if notes:
        note_list = "
".join([f"• {note.name}" for note in notes])
        await message.answer(f"📋 الملاحظات:

{note_list}", parse_mode=None)
    else:
        await message.answer("ℹ️ لا توجد ملاحظات.", parse_mode=None)


@multi_command("delete", "حذف", "امسح", "delnote")
async def delete_note_arabic(message: Message):
    """حذف ملاحظة"""
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("📝 الاستخدام: /حذف <اسم>
مثال: /حذف rules", parse_mode=None)
        return

    name = args[1]
    from app.database.db import delete_note
    if await delete_note(message.chat.id, name):
        await message.answer(f"✅ تم حذف الملاحظة: {name}", parse_mode=None)
    else:
        await message.answer(f"❌ الملاحظة {name} غير موجودة.", parse_mode=None)


@multi_command("filter", "فلتر", "رد_تلقائي", "autoreply")
async def add_filter_arabic(message: Message):
    """إضافة فلتر تلقائي"""
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply(
            "📝 الاستخدام: /فلتر <كلمة> <رد>
"
            "مثال: /فلتر مرحبا أهلاً بك في الجروب!",
            parse_mode=None
        )
        return

    word = args[1]
    reply = args[2]
    from app.database.db import add_filter
    await add_filter(message.chat.id, word, reply)
    await message.answer(f"✅ تم إضافة فلتر: {word}", parse_mode=None)


# ============================================================================
# النقاط والسمعة
# ============================================================================

@multi_command("rank", "مستوى", "رتبة", "level")
async def show_rank_arabic(message: Message):
    """عرض مستوى المستخدم"""
    from app.database.db import get_user_points
    up = await get_user_points(message.chat.id, message.from_user.id)
    if up:
        await message.answer(
            f"📊 مستواك

"
            f"⭐ النقاط: {up.points}
"
            f"💎 السمعة: {up.reputation}",
            parse_mode=None
        )
    else:
        await message.answer("📊 مستواك

⭐ النقاط: 0
💎 السمعة: 0", parse_mode=None)


@multi_command("top", "الأفضل", "أكثر", "leaderboard")
async def show_top_arabic(message: Message):
    """الأكثر نشاطاً"""
    from app.database.db import get_top_users
    users = await get_top_users(message.chat.id, 10)
    if users:
        top_list = []
        for i, up in enumerate(users, 1):
            top_list.append(f"{i}. User ID: {up.user_id} — ⭐ {up.points}")
        await message.answer(
            f"🏆 الأكثر نشاطاً:

" + "
".join(top_list),
            parse_mode=None
        )
    else:
        await message.answer("ℹ️ لا توجد بيانات.", parse_mode=None)


@multi_command("rep", "سمعة", "تقييم", "rate")
async def give_reputation_arabic(message: Message):
    """إعطاء سمعة"""
    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد إعطائه سمعة.", parse_mode=None)
        return

    target = message.reply_to_message.from_user
    from app.database.db import add_reputation
    await add_reputation(message.chat.id, target.id, 1)
    await message.answer(f"💎 تم إعطاء سمعة لـ {target.full_name}", parse_mode=None)


# ============================================================================
# الإعدادات والهمسات
# ============================================================================

@multi_command("settings", "اعدادات", "ضبط", "config")
async def show_settings_arabic(message: Message):
    """لوحة الإعدادات"""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from app.database.db import get_or_create_group_settings

    settings = await get_or_create_group_settings(message.chat.id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👋 الترحيب", callback_data="toggle_welcome")],
        [InlineKeyboardButton(text="🤖 الكابتشا", callback_data="toggle_captcha")],
        [InlineKeyboardButton(text="🔗 حظر الروابط", callback_data="toggle_antilink")],
        [InlineKeyboardButton(text="🛡️ مكافحة السبام", callback_data="toggle_antispam")],
        [InlineKeyboardButton(text="🔒 قفل الوسائط", callback_data="toggle_lock_media")],
    ])

    await message.answer(
        f"⚙️ إعدادات الجروب

"
        f"👋 الترحيب: {'✅' if settings.welcome_enabled else '❌'}
"
        f"🤖 الكابتشا: {'✅' if settings.captcha_enabled else '❌'}
"
        f"🔗 حظر الروابط: {'✅' if settings.antilink_enabled else '❌'}
"
        f"🛡️ مكافحة السبام: {'✅' if settings.antispam_enabled else '❌'}
"
        f"🔒 قفل الوسائط: {'✅' if settings.lock_media else '❌'}",
        reply_markup=kb,
        parse_mode=None
    )


@multi_command("whisper", "همسة", "سر", "secret")
async def send_whisper_arabic(message: Message):
    """همسة خاصة"""
    if not message.reply_to_message:
        await message.reply("📌 رد على رسالة العضو المراد إرسال همسة له.", parse_mode=None)
        return

    args = message.text.split(maxsplit=1)
    text = args[1] if len(args) > 1 else "همسة سرية 🤫"

    target = message.reply_to_message.from_user
    try:
        await bot.send_message(target.id, f"🤫 همسة من {message.from_user.full_name}:

{text}", parse_mode=None)
        await message.answer("✅ تم إرسال الهمسة!", parse_mode=None)
    except Exception:
        await message.answer("❌ لا يمكنني إرسال همسة لهذا العضو. ربما لم يبدأ محادثة معي.", parse_mode=None)


# ============================================================================
# أوامر عامة
# ============================================================================

@multi_command("ping", "بنج", "فحص", "test")
async def ping_arabic(message: Message):
    """فحص البوت"""
    await message.answer("🏓 pong", parse_mode=None)


@multi_command("help", "مساعدة", "اوامر", "commands")
async def help_arabic(message: Message):
    """قائمة الأوامر"""
    help_text = (
        "📋 قائمة الأوامر

"
        "🛡️ الإدارة:
"
        "• /ban /حظر /طرد_نهائي — حظر عضو
"
        "• /unban /فك_الحظر /رفع_الحظر — رفع الحظر
"
        "• /kick /طرد /اخراج — طرد عضو
"
        "• /mute /كتم /سكوت — كتم عضو
"
        "• /unmute /فك_الكتم /رفع_الكتم — رفع الكتم
"
        "• /warn /تحذير /انذار — تحذير عضو
"
        "• /unwarn /حذف_التحذير /مسح_التحذير — مسح التحذيرات
"
        "• /purge /مسح /حذف — حذف رسائل
"
        "• /pin /تثبيت — تثبيت رسالة

"
        "👥 المجموعة:
"
        "• /rules /قوانين /قانون — قوانين الجروب
"
        "• /setrules /تعيين_قوانين — تعيين القوانين
"
        "• /id /ايدي /هوية — معلومات الحساب
"
        "• /info /معلومات /بيانات — معلومات مستخدم
"
        "• /admins /المشرفين /ادمن — قائمة المشرفين
"
        "• /report /تبليغ /بلاغ — تبليغ عن رسالة
"
        "• /link /رابط /لينك — رابط الجروب

"
        "👋 الترحيب والحماية:
"
        "• /setwelcome /تعيين_ترحيب /ترحيب — تعيين ترحيب
"
        "• /welcome /عرض_ترحيب /الترحيب — عرض الترحيب
"
        "• /captcha /كابتشا /تحقق — تفعيل الكابتشا
"
        "• /antilink /حظر_روابط /لینك — حظر الروابط
"
        "• /antispam /مكافحة_سبام /سبام — مكافحة السبام
"
        "• /lock /قفل /اغلاق — قفل وسائط
"
        "• /unlock /فتح /افتح — فتح وسائط

"
        "📝 الملاحظات:
"
        "• /save /حفظ /احفظ — حفظ ملاحظة
"
        "• /get /جلب /عرض — عرض ملاحظة
"
        "• /notes /ملاحظات /قائمة — قائمة الملاحظات
"
        "• /delete /حذف /امسح — حذف ملاحظة
"
        "• /filter /فلتر /رد_تلقائي — فلتر تلقائي

"
        "📊 النقاط:
"
        "• /rank /مستوى /رتبة — مستواك
"
        "• /top /الأفضل /أكثر — الأكثر نشاطاً
"
        "• /rep /سمعة /تقييم — إعطاء سمعة

"
        "⚙️ أخرى:
"
        "• /settings /اعدادات /ضبط — إعدادات الجروب
"
        "• /whisper /همسة /سر — همسة خاصة
"
        "• /ping /بنج /فحص — فحص البوت
"
        "• /help /مساعدة /اوامر — هذه القائمة"
    )
    await message.answer(help_text, parse_mode=None)

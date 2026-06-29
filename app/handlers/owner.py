# app/handlers/owner.py

from pathlib import Path
import shutil
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile, InputProfilePhotoStatic

from app.core.config import settings
from app.core.logger import logger
from app.bot.bot import bot

router = Router()


def is_owner(user_id: int) -> bool:
    return user_id == settings.OWNER_ID


async def owner_only(message: Message) -> bool:
    """التحقق من أن المستخدم هو المالك"""
    if not is_owner(message.from_user.id):
        await message.reply("❌ هذا الأمر للمالك فقط!", parse_mode=None)
        return False
    return True


# ============================================================================
# الأوامر القديمة (موجودة)
# ============================================================================

@router.message(Command("setphoto"))
async def set_bot_photo(message: Message):
    if not await owner_only(message):
        return

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply("رد على صورة وارسل /setphoto لتعيينها كصورة بروفايل للبوت.", parse_mode=None)
        return

    try:
        file_id = message.reply_to_message.photo[-1].file_id
        file = await bot.get_file(file_id)
        downloaded = await bot.download_file(file.file_path)
        photo = FSInputFile(downloaded)
        await bot.delete_my_photo()
        await bot.set_my_profile_photo(
            photo=InputProfilePhotoStatic(photo=photo)
        )
        await message.answer("✅ تم تغيير صورة البوت.", parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}", parse_mode=None)


@router.message(Command("setname"))
async def set_bot_name(message: Message, command: CommandObject):
    if not await owner_only(message):
        return

    name = command.args
    if not name:
        await message.reply("اكتب الاسم بعد الأمر.\nمثال: /setname Mr Bot", parse_mode=None)
        return

    try:
        await bot.set_my_name(name)
        await message.answer(f"✅ تم تغيير اسم البوت إلى: {name}", parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}", parse_mode=None)


@router.message(Command("setdesc"))
async def set_bot_desc(message: Message, command: CommandObject):
    if not await owner_only(message):
        return

    desc = command.args
    if not desc:
        await message.reply("اكتب الوصف بعد الأمر.\nمثال: /setdesc بوت إدارة المجموعات", parse_mode=None)
        return

    try:
        await bot.set_my_description(description=desc)
        await message.answer(f"✅ تم تغيير وصف البوت إلى:\n{desc}", parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}", parse_mode=None)


@router.message(Command("setabout"))
async def set_bot_about(message: Message, command: CommandObject):
    if not await owner_only(message):
        return

    about = command.args
    if not about:
        await message.reply("اكتب النبذة بعد الأمر.\nمثال: /setabout بوت لإدارة الجروبات", parse_mode=None)
        return

    try:
        await bot.set_my_short_description(short_description=about)
        await message.answer(f"✅ تم تغيير نبذة البوت إلى:\n{about}", parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}", parse_mode=None)


@router.message(Command("botinfo"))
async def bot_info(message: Message):
    if not await owner_only(message):
        return

    try:
        me = await bot.get_me()
        text = (
            f"🤖 معلومات البوت\n\n"
            f"📛 الاسم: {me.full_name}\n"
            f"👤 المعرف: @{me.username}\n"
            f"🆔 ID: {me.id}\n"
            f"🔗 الرابط: https://t.me/{me.username}\n\n"
            f"📋 الأوامر المتاحة لك:\n"
            f"• /setphoto — تغيير صورة البوت\n"
            f"• /setname <name> — تغيير اسم البوت\n"
            f"• /setdesc <text> — تغيير وصف البوت\n"
            f"• /setabout <text> — تغيير نبذة البوت\n"
            f"• /botinfo — عرض معلومات البوت\n"
            f"• /broadcast <text> — إرسال رسالة لكل المجموعات\n"
            f"• /stats — إحصائيات البوت\n"
            f"• /groups — قائمة الجروبات\n"
            f"• /backup — نسخة احتياطية\n"
            f"• /restart — إعادة تشغيل\n"
            f"• /logs — عرض السجلات"
        )
        await message.answer(text, parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ خطأ: {e}", parse_mode=None)


@router.message(Command("broadcast"))
async def broadcast(message: Message, command: CommandObject):
    if not await owner_only(message):
        return

    text = command.args
    if not text:
        await message.reply("اكتب الرسالة بعد الأمر.\nمثال: /broadcast مرحباً للجميع", parse_mode=None)
        return

    from app.database.db import get_all_groups
    groups = await get_all_groups()

    if not groups:
        await message.answer("لا توجد مجموعات مسجلة.", parse_mode=None)
        return

    sent = 0
    failed = 0
    for g in groups:
        try:
            await bot.send_message(g.group_id, f"📢 إعلان من المالك:\n\n{text}", parse_mode=None)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(
        f"📊 نتيجة الإرسال:\n\n"
        f"✅ نجح: {sent}\n"
        f"❌ فشل: {failed}\n"
        f"📋 المجموع: {len(groups)}",
        parse_mode=None
    )


# ============================================================================
# الأوامر الجديدة
# ============================================================================

@router.message(Command("stats"))
@router.message(Command("إحصائيات"))
@router.message(Command("احصائيات"))
async def bot_stats(message: Message):
    """إحصائيات البوت"""
    if not await owner_only(message):
        return
    
    from app.database.db import get_all_groups
    from app.database.session import AsyncSessionLocal
    from app.database.models import User, GroupSettings, Log
    from sqlalchemy import func
    
    async with AsyncSessionLocal() as db:
        # عدد المستخدمين
        users_count = await db.execute(func.count(User.id))
        users_total = users_count.scalar()
        
        # عدد الجروبات
        groups = await get_all_groups()
        groups_count = len(groups)
        
        # عدد السجلات
        logs_count = await db.execute(func.count(Log.id))
        logs_total = logs_count.scalar()
    
    text = (
        f"📊 إحصائيات البوت\n\n"
        f"👥 إجمالي المستخدمين: {users_total}\n"
        f"💬 عدد الجروبات: {groups_count}\n"
        f"📋 إجمالي السجلات: {logs_total}\n"
        f"🤖 اسم البوت: {settings.BOT_NAME}\n"
        f"👑 المالك: {settings.OWNER_ID}"
    )
    
    await message.answer(text, parse_mode=None)


@router.message(Command("groups"))
@router.message(Command("جروباتي"))
@router.message(Command("قائمة_جروبات"))
async def list_groups(message: Message):
    """قائمة الجروبات المسجلة"""
    if not await owner_only(message):
        return
    
    groups = await get_all_groups()
    
    if not groups:
        await message.answer("ℹ️ لا توجد جروبات مسجلة.", parse_mode=None)
        return
    
    text = "📋 قائمة الجروبات:\n\n"
    for i, group in enumerate(groups, 1):
        text += f"{i}. {group.title or 'بدون اسم'} (ID: {group.group_id})\n"
    
    await message.answer(text, parse_mode=None)


@router.message(Command("leave"))
@router.message(Command("مغادرة"))
@router.message(Command("اخرج"))
async def leave_group(message: Message, command: CommandObject):
    """مغادرة جروب"""
    if not await owner_only(message):
        return
    
    chat_id = command.args
    if not chat_id:
        await message.reply(
            "📝 الاستخدام: /leave <chat_id>\n"
            "أو: /مغادرة <chat_id>\n\n"
            "سيتم خروج البوت من الجروب المحدد.",
            parse_mode=None
        )
        return
    
    try:
        await bot.leave_chat(chat_id)
        await message.answer(f"✅ تم مغادرة الجروب: {chat_id}", parse_mode=None)
        from app.database.db import add_log
        await add_log(0, message.from_user.id, f"leave {chat_id}")
    except Exception as e:
        await message.answer(f"❌ تعذر مغادرة الجروب: {e}", parse_mode=None)


@router.message(Command("backup"))
@router.message(Command("نسخة_احتياطية"))
@router.message(Command("احفظ"))
async def backup_database(message: Message):
    """نسخ احتياطي لقاعدة البيانات"""
    if not await owner_only(message):
        return
    
    try:
        # نسخ ملف قاعدة البيانات
        source = "data/mrbot.db"
        backup_name = f"data/mrbot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(source, backup_name)
        
        # إرسال الملف
        document = FSInputFile(backup_name)
        await message.reply_document(
            document,
            caption=f"✅ تم إنشاء نسخة احتياطية!\n📁 {backup_name}",
            parse_mode=None
        )
        
        from app.database.db import add_log
        await add_log(0, message.from_user.id, f"backup: {backup_name}")
    except Exception as e:
        await message.answer(f"❌ فشل إنشاء النسخة الاحتياطية: {e}", parse_mode=None)


@router.message(Command("restart"))
@router.message(Command("إعادة_تشغيل"))
@router.message(Command("ريستارت"))
async def restart_bot(message: Message):
    """إعادة تشغيل البوت"""
    if not await owner_only(message):
        return
    
    await message.answer("🔄 جاري إعادة تشغيل البوت...", parse_mode=None)
    from app.database.db import add_log
    await add_log(0, message.from_user.id, "restart requested")
    
    # إعادة تشغيل (في Docker ستعمل تلقائياً)
    import sys
    sys.exit(0)


@router.message(Command("logs"))
@router.message(Command("سجلات"))
@router.message(Command("السجلات"))
async def show_logs(message: Message):
    """عرض آخر السجلات"""
    if not await owner_only(message):
        return
    
    try:
        with open("logs/mrbot.log", "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_lines = lines[-50:]  # آخر 50 سطر
        
        text = "📋 آخر السجلات:\n\n"
        text += "".join(last_lines)
        
        if len(text) > 4000:
            # إرسال كملف
            with open("logs/last_logs.txt", "w", encoding="utf-8") as f:
                f.write(text)
            
            document = FSInputFile("logs/last_logs.txt")
            await message.reply_document(document, caption="📋 آخر السجلات", parse_mode=None)
        else:
            await message.answer(text, parse_mode=None)
    except Exception as e:
        await message.answer(f"❌ تعذر قراءة السجلات: {e}", parse_mode=None)

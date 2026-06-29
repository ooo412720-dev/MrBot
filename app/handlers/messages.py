# app/handlers/messages.py

import random
import re

from aiogram import Router, F
from aiogram.types import Message

from app.bot.bot import bot
from app.core.logger import logger
from app.database.db import (
    get_or_create_group_settings, 
    add_points, 
    get_filters,
    get_or_create_user,
    get_user_points
)

router = Router()

# ============================================================================
# القوائم
# ============================================================================

GREETINGS = ["السلام عليكم", "سلام عليكم", "هلا", "مرحبا", "مرحبًا", "اهلا", "أهلاً", "هاي", "صباح الخير", "مساء الخير", "هلو", "hello", "hi"]
GREETING_REPLIES = [
    "وعليكم السلام ورحمة الله 🌟", "أهلاً وسهلاً بك! 👋", "مرحباً بك يا صديقي! 😊",
    "هلا والله! 🌹", "نوّرتنا! ✨", "أهلاً {name}! 🌟",
]

THANKS = ["شكرا", "شكراً", "مشكور", "ممتن", "تسلم", "تسلمين", "شكر", "thanks", "thank you"]
THANKS_REPLIES = ["العفو! 🌸", "لا شكر على واجب! 😊", "أهلاً بك دائماً! 🌟", "تسلم أنت! 🙏", "العفو يا {name}! 💕"]

BYE = ["باي", "مع السلامة", "وداعا", "وداعاً", "تصبح على خير", "bye", "goodbye", "see you"]
BYE_REPLIES = ["مع السلامة! 👋", "إلى اللقاء! 🌹", "تصبح على خير! 🌙", "في أمان الله! 🤲", "مع السلامة يا {name}! 👋"]

LOVE = ["بحبك", "أحبك", "حبيبي", "حبيبتي", "love you", "i love you"]
LOVE_REPLIES = ["وأنا أحبك أكثر! ❤️", "يا قلبي النابض! 💕", "أنت الأحب! 🌹", "حبيبي أنت! 💖"]

QUESTION_PATTERNS = [
    (r"كيف حالك", "الحمد لله بخير! وأنت كيف حالك؟ 😊"),
    (r"ما اسمك", "اسمي MrBot! أنا بوت إدارة المجموعات 🤖"),
    (r"من انت", "أنا MrBot، بوت ذكي لإدارة الجروبات! 🤖"),
    (r"من أنت", "أنا MrBot، بوت ذكي لإدارة الجروبات! 🤖"),
    (r"شلونك", "الحمد لله بخير! وأنت شلونك؟ 😊"),
    (r"اخبارك", "الحمد لله تمام! وأنت كيف أخبارك؟ 🌟"),
    (r"كم الساعة", "الساعة الآن... لا عندي ساعة 😅 لكن ابحث في جهازك!"),
    (r"فينك", "أنا هنا دائماً! في خدمتك 24/7 🤖"),
    (r"وينك", "أنا هنا دائماً! في خدمتك 24/7 🤖"),
]

FUN_REPLIES = ["😂", "🤣", "👍", "💪", "🔥", "✨", "👀", "🎯", "🚀", "💯"]

# كلمات مناداة البوت
BOT_MENTIONS = ["بوت", "mrbot", "mr bot", "مستر بوت", "mr_adam", "mradam"]

# ============================================================================
# دوال مساعدة
# ============================================================================

def format_reply(reply: str, name: str) -> str:
    """تنسيق الرد باسم المستخدم"""
    return reply.replace("{name}", name)


async def send_whisper(message: Message):
    """إرسال همسة خاصة"""
    if not message.reply_to_message:
        await message.reply(
            "📌 لإرسال همسة، رد على رسالة العضو المراد إرسال همسة له.\n"
            "ثم اكتب: همسه أو همسة",
            parse_mode=None
        )
        return False
    
    target = message.reply_to_message.from_user
    try:
        await bot.send_message(
            target.id,
            f"🤫 همسة سرية من {message.from_user.full_name} في {message.chat.title or 'الجروب'}!\n\n"
            f"اكتب /start لبدء محادثة معي للرد.",
            parse_mode=None
        )
        await message.reply("✅ تم إرسال الهمسة سراً! 🤫", parse_mode=None)
        return True
    except Exception as e:
        logger.warning(f"Whisper failed: {e}")
        await message.reply(
            "❌ لا يمكنني إرسال همسة لهذا العضو.\n"
            "🔰 السبب: لم يبدأ محادثة معي في الخاص.\n"
            "💡 الحل: اطلب منه إرسال /start لي في الخاص.",
            parse_mode=None
        )
        return False


async def show_user_info(message: Message):
    """عرض معلومات المستخدم"""
    user = message.from_user
    chat = message.chat
    
    # تسجيل المستخدم
    await get_or_create_user(user.id, user.username, user.full_name)
    
    # الحصول على النقاط
    points_data = await get_user_points(chat.id, user.id) if chat.type in ("group", "supergroup") else None
    
    text = (
        f"📋 معلومات حسابك\n\n"
        f"👤 الاسم: {user.full_name}\n"
        f"🆔 ID: {user.id}\n"
    )
    
    if user.username:
        text += f"🔗 Username: @{user.username}\n"
    
    text += f"📛 النوع: {chat.type}\n"
    
    if chat.type in ("group", "supergroup"):
        text += f"💬 Chat ID: {chat.id}\n"
        if points_data:
            text += f"⭐ النقاط: {points_data.points}\n"
            text += f"💎 السمعة: {points_data.reputation}\n"
        else:
            text += f"⭐ النقاط: 0\n💎 السمعة: 0\n"
    
    # صلاحيات المستخدم
    if chat.type in ("group", "supergroup"):
        try:
            member = await bot.get_chat_member(chat.id, user.id)
            status_map = {
                "creator": "👑 المالك",
                "administrator": "🔧 مشرف",
                "member": "👤 عضو",
                "restricted": "⚠️ مقيد",
                "left": "🚫 غادر",
                "kicked": "🚫 محظور"
            }
            status = status_map.get(member.status, member.status)
            text += f"🛡️ الصلاحية: {status}\n"
            
            if member.status == "administrator":
                text += "\n🔧 صلاحياتك:\n"
                if member.can_manage_chat:
                    text += "  ✅ إدارة الجروب\n"
                if member.can_delete_messages:
                    text += "  ✅ حذف الرسائل\n"
                if member.can_manage_video_chats:
                    text += "  ✅ إدارة المكالمات\n"
                if member.can_restrict_members:
                    text += "  ✅ تقييد الأعضاء\n"
                if member.can_promote_members:
                    text += "  ✅ ترقية الأعضاء\n"
                if member.can_change_info:
                    text += "  ✅ تعديل المعلومات\n"
                if member.can_invite_users:
                    text += "  ✅ دعوة مستخدمين\n"
                if member.can_post_messages:
                    text += "  ✅ نشر رسائل\n"
                if member.can_edit_messages:
                    text += "  ✅ تعديل رسائل\n"
                if member.can_pin_messages:
                    text += "  ✅ تثبيت رسائل\n"
        except Exception as e:
            logger.warning(f"Could not get member info: {e}")
    
    await message.reply(text, parse_mode=None)


# ============================================================================
# المعالج الرئيسي
# ============================================================================

@router.message(F.text)
async def handle_message(message: Message):
    """المعالج الرئيسي للرسائل النصية"""
    
    # التحقق من نوع الدردشة
    if message.chat.type not in ("group", "supergroup", "private"):
        return
    
    # تجاهل رسائل البوتات
    if message.from_user.is_bot:
        return
    
    text = message.text.strip()
    text_lower = text.lower()
    user_name = message.from_user.full_name
    
    # ============================================================================
    # 1. أوامر خاصة بالنص العادي (بدون /)
    # ============================================================================
    
    # همسة
    if text_lower in ["همسه", "همسة", "سر", "whisper"]:
        await send_whisper(message)
        return
    
    # صلاحياتي / معلوماتي
    if text_lower in ["صلاحياتي", "معلوماتي", "حسابي", "ايدي", "id", "myinfo"]:
        await show_user_info(message)
        return
    
    # ============================================================================
    # 2. فلاتر مخصصة
    # ============================================================================
    
    if message.chat.type in ("group", "supergroup"):
        try:
            filters = await get_filters(message.chat.id)
            for f in filters:
                if f.word.lower() in text_lower:
                    await message.reply(f.reply, parse_mode=None)
                    return
        except Exception as e:
            logger.warning(f"Filter error: {e}")
    
    # ============================================================================
    # 3. مناداة البوت
    # ============================================================================
    
    for mention in BOT_MENTIONS:
        if mention in text_lower:
            # رد عشوائي على مناداة البوت
            replies = [
                f"نعم {user_name}؟ 🤖",
                f"أنا هنا! كيف يمكنني مساعدتك؟ 😊",
                f"أمرك يا {user_name}! 🫡",
                f"أنا في خدمتك! 🚀",
                f"نعم، أنا MrBot! 🤖",
            ]
            await message.reply(random.choice(replies), parse_mode=None)
            return
    
    # ============================================================================
    # 4. التحيات
    # ============================================================================
    
    for g in GREETINGS:
        if g in text_lower:
            reply = random.choice(GREETING_REPLIES)
            await message.reply(format_reply(reply, user_name), parse_mode=None)
            return
    
    # ============================================================================
    # 5. الشكر
    # ============================================================================
    
    for t in THANKS:
        if t in text_lower:
            reply = random.choice(THANKS_REPLIES)
            await message.reply(format_reply(reply, user_name), parse_mode=None)
            return
    
    # ============================================================================
    # 6. الوداع
    # ============================================================================
    
    for b in BYE:
        if b in text_lower:
            reply = random.choice(BYE_REPLIES)
            await message.reply(format_reply(reply, user_name), parse_mode=None)
            return
    
    # ============================================================================
    # 7. الحب
    # ============================================================================
    
    for l in LOVE:
        if l in text_lower:
            reply = random.choice(LOVE_REPLIES)
            await message.reply(format_reply(reply, user_name), parse_mode=None)
            return
    
    # ============================================================================
    # 8. الأسئلة الشائعة
    # ============================================================================
    
    for pattern, reply in QUESTION_PATTERNS:
        if re.search(pattern, text_lower):
            await message.reply(reply, parse_mode=None)
            return
    
    # ============================================================================
    # 9. ردود ممتعة عشوائية (5% احتمال)
    # ============================================================================
    
    if not text.startswith("/") and len(text) > 3 and random.random() < 0.05:
        await message.reply(random.choice(FUN_REPLIES), parse_mode=None)
        return
    
    # ============================================================================
    # 10. إضافة نقاط تلقائية
    # ============================================================================
    
    if message.chat.type in ("group", "supergroup") and not text.startswith("/"):
        try:
            await add_points(message.chat.id, message.from_user.id, amount=1)
        except Exception as e:
            logger.warning(f"Points error: {e}")

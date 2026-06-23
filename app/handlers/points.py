# app/handlers/points.py

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from app.database.db import (
    add_points, add_reputation, get_user_points, get_top_users
)

router = Router()


def get_level(points: int) -> int:
    return points // 100


def get_rank_name(level: int) -> str:
    if level >= 20:
        return "👑 أسطورة"
    elif level >= 15:
        return "💎 خبير"
    elif level >= 10:
        return "🔥 محترف"
    elif level >= 5:
        return "⭐ متقدم"
    elif level >= 1:
        return "🌱 مبتدئ"
    else:
        return "🆕 جديد"


@router.message(Command("rank"))
async def show_rank(message: Message):
    up = await get_user_points(message.chat.id, message.from_user.id)
    points = up.points if up else 0
    reputation = up.reputation if up else 0
    level = get_level(points)
    rank_name = get_rank_name(level)

    progress = points % 100
    bar_filled = progress // 10
    bar = "█" * bar_filled + "░" * (10 - bar_filled)

    await message.answer(
        f"📊 **مستواك**\n\n"
        f"👤 الاسم: {message.from_user.full_name}\n"
        f"🏆 الرتبة: {rank_name}\n"
        f"📈 المستوى: {level}\n"
        f"⭐ النقاط: {points}\n"
        f"💫 السمعة: {reputation}\n"
        f"\nالتقدم للمستوى التالي:\n`{bar}` {progress}/100"
    )


@router.message(Command("top"))
async def show_top(message: Message):
    top_users = await get_top_users(message.chat.id, limit=10)
    if not top_users:
        await message.answer("ℹ️ لا توجد بيانات بعد.")
        return

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = []
    for i, up in enumerate(top_users):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        lines.append(f"{medal} `{up.user_id}` — {up.points} نقطة")

    await message.answer(
        "🏆 **الأكثر نشاطاً**\n\n" + "\n".join(lines)
    )


@router.message(Command("rep"))
async def give_reputation(message: Message):
    if not message.reply_to_message:
        await message.reply("رد على رسالة الشخص الذي تريد إعطاءه سمعة.")
        return

    target = message.reply_to_message.from_user
    if target.id == message.from_user.id:
        await message.answer("⚠️ لا يمكنك إعطاء سمعة لنفسك.")
        return

    await add_reputation(message.chat.id, target.id)
    await message.answer(f"💫 {message.from_user.full_name} أعطى سمعة إلى {target.full_name}!")


@router.message(F.text)
async def auto_points(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    if message.from_user.is_bot:
        return

    text = message.text.strip()
    if text.startswith("/"):
        return

    await add_points(message.chat.id, message.from_user.id, amount=1)

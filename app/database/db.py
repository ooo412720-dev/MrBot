# app/database/db.py

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    User, GroupSettings, Note, FilteredWord,
    Warning, Mute, UserPoints, Log, Captcha
)
from app.database.session import AsyncSessionLocal


async def init_db():
    from app.database.base import Base
    from app.database.session import async_engine
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create_user(telegram_id: int, username: str | None, first_name: str) -> User:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # ✅ المستخدم موجود - تحديث البيانات فقط
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if updated:
                await db.commit()
            return user
        
        # ✅ إنشاء مستخدم جديد
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def get_or_create_group_settings(group_id: int, title: str | None = None) -> GroupSettings:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GroupSettings).where(GroupSettings.group_id == group_id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            settings = GroupSettings(group_id=group_id, title=title)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        return settings


async def update_group_setting(group_id: int, key: str, value):
    async with AsyncSessionLocal() as db:
        await db.execute(
            update(GroupSettings)
            .where(GroupSettings.group_id == group_id)
            .values(**{key: value})
        )
        await db.commit()


async def save_note(group_id: int, name: str, content: str, user_id: int):
    async with AsyncSessionLocal() as db:
        existing = await db.execute(
            select(Note).where(Note.group_id == group_id, Note.name == name)
        )
        note = existing.scalar_one_or_none()
        if note:
            note.content = content
            note.created_by = user_id
        else:
            note = Note(
                group_id=group_id, name=name,
                content=content, created_by=user_id
            )
            db.add(note)
        await db.commit()


async def get_note(group_id: int, name: str) -> Note | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Note).where(Note.group_id == group_id, Note.name == name)
        )
        return result.scalar_one_or_none()


async def get_notes(group_id: int) -> list[Note]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Note).where(Note.group_id == group_id)
        )
        return list(result.scalars().all())


async def delete_note(group_id: int, name: str) -> bool:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            delete(Note).where(Note.group_id == group_id, Note.name == name)
        )
        await db.commit()
        return result.rowcount > 0


async def add_filter(group_id: int, word: str, reply: str):
    async with AsyncSessionLocal() as db:
        existing = await db.execute(
            select(FilteredWord).where(
                FilteredWord.group_id == group_id,
                FilteredWord.word == word
            )
        )
        fw = existing.scalar_one_or_none()
        if fw:
            fw.reply = reply
        else:
            fw = FilteredWord(group_id=group_id, word=word, reply=reply)
            db.add(fw)
        await db.commit()


async def get_filters(group_id: int) -> list[FilteredWord]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(FilteredWord).where(FilteredWord.group_id == group_id)
        )
        return list(result.scalars().all())


async def add_warning(group_id: int, user_id: int, reason: str | None = None) -> int:
    async with AsyncSessionLocal() as db:
        w = Warning(group_id=group_id, user_id=user_id, reason=reason)
        db.add(w)
        await db.commit()
        count_result = await db.execute(
            select(func.count(Warning.id)).where(
                Warning.group_id == group_id,
                Warning.user_id == user_id
            )
        )
        return count_result.scalar()


async def clear_warnings(group_id: int, user_id: int):
    async with AsyncSessionLocal() as db:
        await db.execute(
            delete(Warning).where(
                Warning.group_id == group_id,
                Warning.user_id == user_id
            )
        )
        await db.commit()


async def get_warnings_count(group_id: int, user_id: int) -> int:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count(Warning.id)).where(
                Warning.group_id == group_id,
                Warning.user_id == user_id
            )
        )
        return result.scalar()


async def add_points(group_id: int, user_id: int, amount: int = 1):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserPoints).where(
                UserPoints.group_id == group_id,
                UserPoints.user_id == user_id
            )
        )
        up = result.scalar_one_or_none()
        if up:
            up.points += amount
        else:
            up = UserPoints(group_id=group_id, user_id=user_id, points=amount)
            db.add(up)
        await db.commit()


async def add_reputation(group_id: int, user_id: int, amount: int = 1):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserPoints).where(
                UserPoints.group_id == group_id,
                UserPoints.user_id == user_id
            )
        )
        up = result.scalar_one_or_none()
        if up:
            up.reputation += amount
        else:
            up = UserPoints(group_id=group_id, user_id=user_id, reputation=amount)
            db.add(up)
        await db.commit()


async def get_user_points(group_id: int, user_id: int) -> UserPoints | None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserPoints).where(
                UserPoints.group_id == group_id,
                UserPoints.user_id == user_id
            )
        )
        return result.scalar_one_or_none()


async def get_top_users(group_id: int, limit: int = 10) -> list[UserPoints]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserPoints)
            .where(UserPoints.group_id == group_id)
            .order_by(UserPoints.points.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


async def add_log(group_id: int, user_id: int, action: str):
    async with AsyncSessionLocal() as db:
        log = Log(group_id=group_id, user_id=user_id, action=action)
        db.add(log)
        await db.commit()


async def get_all_groups() -> list[GroupSettings]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(GroupSettings)
        )
        return list(result.scalars().all())


async def save_captcha(user_id: int, group_id: int, answer: str):
    async with AsyncSessionLocal() as db:
        c = Captcha(user_id=user_id, group_id=group_id, answer=answer)
        db.add(c)
        await db.commit()


async def verify_captcha(user_id: int, group_id: int, answer: str) -> bool:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Captcha).where(
                Captcha.user_id == user_id,
                Captcha.group_id == group_id
            ).order_by(Captcha.created_at.desc()).limit(1)
        )
        c = result.scalar_one_or_none()
        if c and c.answer == answer:
            await db.delete(c)
            await db.commit()
            return True
        return False

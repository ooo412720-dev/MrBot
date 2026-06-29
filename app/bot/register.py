# app/bot/register.py

from app.bot.dispatcher import dp
from app.handlers.commands import router as commands_router
from app.handlers.owner import router as owner_router
from app.handlers.admin import router as admin_router
from app.handlers.group import router as group_router
from app.handlers.welcome import router as welcome_router
from app.handlers.protection import router as protection_router
from app.handlers.notes import router as notes_router
from app.handlers.points import router as points_router
from app.handlers.settings import router as settings_router
from app.handlers.whispers import router as whispers_router
from app.handlers.messages import router as messages_router
from app.handlers.start import router as start_router
from app.handlers.group_commands import router as group_commands_router
from app.handlers.arabic_commands import router as arabic_commands_router  # جديد

def register_handlers():
    dp.include_router(owner_router)
    dp.include_router(commands_router)
    dp.include_router(admin_router)
    dp.include_router(group_router)
    dp.include_router(welcome_router)
    dp.include_router(protection_router)
    dp.include_router(notes_router)
    dp.include_router(points_router)
    dp.include_router(settings_router)
    dp.include_router(whispers_router)
    dp.include_router(start_router)
    dp.include_router(group_commands_router)
    dp.include_router(arabic_commands_router)  # جديد - أضف قبل messages_router
    dp.include_router(messages_router)

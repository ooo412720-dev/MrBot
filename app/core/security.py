# app/core/security.py

from app.core.config import settings


def validate_environment():

    if not settings.BOT_TOKEN:

        raise Exception(
            "BOT_TOKEN missing"
        )

    if len(settings.BOT_TOKEN) < 20:

        raise Exception(
            "BOT_TOKEN invalid"
        )
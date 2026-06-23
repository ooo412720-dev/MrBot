# app/core/sentry.py

import sentry_sdk
from app.core.config import settings


def init_sentry():
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0
        )


init_sentry()

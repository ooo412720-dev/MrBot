# app/bot/setup.py

from app.bot.dispatcher import dp
from app.bot.middlewares import LoggingMiddleware
from app.bot.rate_limit_middleware import RateLimitMiddleware
from app.bot.metrics_middleware import MetricsMiddleware


def setup_middlewares():
    for mw in (LoggingMiddleware(), RateLimitMiddleware(), MetricsMiddleware()):
        dp.message.middleware(mw)
        dp.callback_query.middleware(mw)

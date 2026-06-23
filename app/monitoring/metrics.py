# app/monitoring/metrics.py

from prometheus_client import Counter


MESSAGES_COUNTER = Counter(

    "telegram_messages_total",

    "Total telegram messages"
)
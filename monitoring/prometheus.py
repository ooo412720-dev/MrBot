from prometheus_client import Counter

MESSAGES = Counter(
    "messages_total",
    "Total messages"
)
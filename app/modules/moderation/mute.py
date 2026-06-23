from datetime import datetime, timedelta, timezone


def mute_for_hour():
    return datetime.now(timezone.utc) + timedelta(hours=1)

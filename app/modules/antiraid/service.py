from collections import defaultdict
from time import time

RAID_LIMIT = 20
WINDOW = 60

raid_cache = defaultdict(list)


def detect_raid(group_id: int) -> bool:

    now = time()

    raid_cache[group_id].append(now)

    # حذف السجلات القديمة
    raid_cache[group_id] = [
        timestamp
        for timestamp in raid_cache[group_id]
        if now - timestamp <= WINDOW
    ]

    return len(
        raid_cache[group_id]
    ) >= RAID_LIMIT
from collections import defaultdict
from time import time

# عدد الملصقات المسموح بها
MAX_STICKERS = 5

# مدة الفحص بالثواني
STICKER_WINDOW = 15

# عدد مرات تكرار نفس الملصق
MAX_REPEAT = 3

# مدة فحص التكرار
REPEAT_WINDOW = 30

# تخزين الملصقات
# user_id -> [(sticker_id, timestamp)]
sticker_cache = defaultdict(list)


def detect_sticker_spam(
    user_id: int,
    sticker_id: str
) -> bool:

    now = time()

    sticker_cache[user_id].append(
        (sticker_id, now)
    )

    # حذف السجلات القديمة
    sticker_cache[user_id] = [
        item
        for item in sticker_cache[user_id]
        if now - item[1] <= STICKER_WINDOW
    ]

    return (
        len(sticker_cache[user_id])
        >= MAX_STICKERS
    )


def repeated_sticker(
    user_id: int,
    sticker_id: str
) -> bool:

    now = time()

    recent = [
        sticker
        for sticker, timestamp
        in sticker_cache[user_id]
        if now - timestamp <= REPEAT_WINDOW
    ]

    repeated_count = recent.count(
        sticker_id
    )

    return (
        repeated_count
        >= MAX_REPEAT
    )


def clear_user_stickers(
    user_id: int
) -> None:

    if user_id in sticker_cache:
        del sticker_cache[user_id]
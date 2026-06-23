from app.modules.ai_filter.service import (
    normalize_text
)

SPAM_PATTERNS = [
    "free",
    "gift",
    "earn",
    "crypto",
    "airdrop",
    "مجانا",
    "هدية",
    "اربح",
    "ايردروب",
    "عملات"
]


def spam_score(text: str) -> tuple[int, list[str]]:

    normalized = normalize_text(text)

    score = 0
    matches = []

    for pattern in SPAM_PATTERNS:

        if pattern in normalized:

            score += 20
            matches.append(pattern)

    return score, matches
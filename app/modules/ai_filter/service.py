import re


def normalize_text(text: str) -> str:

    text = text.lower()

    text = re.sub(
        r"[^\w\s]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        "",
        text
    )

    return text


def looks_like_spam(text: str) -> bool:

    normalized = normalize_text(
        text
    )

    keywords = [
        "free",
        "join",
        "earn",
        "gift"
    ]

    return any(
        word in normalized
        for word in keywords
    )
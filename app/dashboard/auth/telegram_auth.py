# app/dashboard/auth/telegram_auth.py

import hashlib
import hmac


def verify_telegram_auth(data: dict, bot_token: str) -> bool:
    check_hash = data.get("hash")
    if not check_hash:
        return False

    data_check_string = "\n".join(
        f"{k}={v}"
        for k, v in sorted(data.items())
        if k != "hash"
    )

    secret_key = hashlib.sha256(bot_token.encode()).digest()

    computed_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_hash, check_hash)

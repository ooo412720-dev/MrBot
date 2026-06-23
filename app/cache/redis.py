# app/cache/redis.py
# بديل Redis — يستخدم الذاكرة بدلاً من Redis

import time
from collections import defaultdict

_memory: dict[str, str] = {}
_expiry: dict[str, float] = {}


class FakeRedis:
    async def get(self, key: str) -> str | None:
        if key in _expiry and _expiry[key] < time.time():
            _memory.pop(key, None)
            _expiry.pop(key, None)
            return None
        return _memory.get(key)

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        _memory[key] = value
        if ex:
            _expiry[key] = time.time() + ex

    async def incr(self, key: str) -> int:
        val = int(_memory.get(key, "0")) + 1
        _memory[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int) -> None:
        _expiry[key] = time.time() + seconds

    async def ping(self) -> bool:
        return True

    async def close(self) -> None:
        pass

    async def publish(self, channel: str, message: str) -> None:
        pass


redis_client = FakeRedis()
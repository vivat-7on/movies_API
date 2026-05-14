from redis.asyncio import Redis

from auth.ports.cache.rate_limit import IRateLimitRepo

INCREMENT_AND_GET_SCRIPT = """
local current = redis.call("INCR", KEYS[1])
if current == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end
return current
"""


class RateLimitRepo(IRateLimitRepo):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def increment_and_get(self, key: str, ttl: int) -> int:
        result = await self.redis.eval(
            INCREMENT_AND_GET_SCRIPT,
            1,
            key,
            str(ttl),
        )
        return int(result)

    async def get(self, key: str) -> int | None:
        value = await self.redis.get(key)

        if value is None:
            return None

        return int(value)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

from redis.asyncio import Redis

from auth.ports.cache.state import ICacheStateRepo

GET_DELETE_SCRIPT = """
local value = redis.call("GET", KEYS[1])
if value then
    redis.call("DEL", KEYS[1])
end
return value
"""


class CacheStateRepo(ICacheStateRepo):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def set(self, key: str, value: str, ttl: int) -> None:
        await self.redis.set(key, value, ex=ttl)

    async def get_delete(self, key: str) -> str | None:
        result = await self.redis.eval(
            GET_DELETE_SCRIPT,
            1,
            key,
        )
        return result

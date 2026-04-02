from redis.asyncio import Redis

from models.film import Person
from repositories.cache.base import BaseCacheRepository


class PersonCacheRepository(BaseCacheRepository[Person]):
    def __init__(self, redis: Redis):
        super().__init__(
            redis,
            model=Person,
            key_prefix="person",
            )

from redis.asyncio import Redis
from models.film import Film
from repositories.cache.base import BaseCacheRepository


class FilmCacheRepository(BaseCacheRepository[Film]):
    def __init__(self, redis: Redis):
        super().__init__(
            redis,
            model=Film,
            key_prefix="film",
            )

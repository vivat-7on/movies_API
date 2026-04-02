from redis.asyncio import Redis

from models.film import Genre
from repositories.cache.base import BaseCacheRepository


class GenreCacheRepository(BaseCacheRepository[Genre]):
    def __init__(self, redis: Redis):
        super().__init__(
            redis,
            model=Genre,
            key_prefix="genre",
            )

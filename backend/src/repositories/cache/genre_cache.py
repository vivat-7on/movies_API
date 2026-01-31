import json

from redis.asyncio import Redis

from models.film import Genre

GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
LIST_GENRE_CACHE_EXPIRE_IN_SECONDS = 60  # 1 минута


class GenreCacheRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, genre_id: str) -> Genre | None:
        key = f"genre:{genre_id}"
        data = await self.redis.get(key)
        if not data:
            return None
        genre = Genre.model_validate_json(data)
        return genre

    async def put(self, genre: Genre) -> None:
        await self.redis.set(
            f"genre:{genre.id}",
            genre.model_dump_json(),
            GENRE_CACHE_EXPIRE_IN_SECONDS,
            )

    async def get_list(self, key: str) -> tuple[int, list[Genre]] | None:
        data = await self.redis.get(key)
        if not data:
            return None

        obj = json.loads(data)
        total = obj["total"]
        genres = [Genre(**genre) for genre in obj["genres"]]
        return total, genres

    async def put_list(self, key: str, value: tuple[int, list[Genre]]) -> None:
        total, genres = value
        payload = {
            "total": total,
            "genres": [genre.model_dump() for genre in genres],
            }
        await self.redis.set(
            key,
            json.dumps(payload),
            LIST_GENRE_CACHE_EXPIRE_IN_SECONDS,
            )

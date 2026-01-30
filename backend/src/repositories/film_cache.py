import json

from redis.asyncio import Redis

from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
LIST_CACHE_EXPIRE_IN_SECONDS = 60  # 1 минута


class FilmCacheRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, film_id: str) -> Film | None:
        key = f"film:{film_id}"
        data = await self.redis.get(key)
        if not data:
            return None

        film = Film.model_validate_json(data)
        return film

    async def put(self, film: Film) -> None:
        await self.redis.set(
            f"film:{film.id}",
            film.model_dump_json(),
            FILM_CACHE_EXPIRE_IN_SECONDS,
            )

    async def get_list(self, key: str) -> tuple[int, list[Film]] | None:
        data = await self.redis.get(key)
        if not data:
            return None

        obj = json.loads(data)
        total = obj["total"]
        films = [Film(**film) for film in obj["films"]]
        return total, films

    async def put_list(self, key: str, value: tuple[int, list[Film]]) -> None:
        total, films = value
        payload = {
            "total": total,
            "films": [film.model_dump() for film in films],
            }
        await self.redis.set(
            key,
            json.dumps(payload),
            LIST_CACHE_EXPIRE_IN_SECONDS,
            )

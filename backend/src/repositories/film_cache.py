from redis.asyncio import Redis

from models.film import Film

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут

class FilmCacheRepository:
    def __init__(self, redis:  Redis):
        self.redis = redis

    async def get(self, film_id: str) -> Film | None:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.model_validate_json(data)
        return film

    async def put(self, film: Film) -> None:
        await self.redis.set(
            film.id,
            film.model_dump_json(),
            FILM_CACHE_EXPIRE_IN_SECONDS,
        )
from attrs import frozen
from models.film import Film
from repositories.film_cache import FilmCacheRepository
from repositories.film_elastic import FilmElasticRepository


@frozen
class FilmService:
    elastic_repo: FilmElasticRepository
    cache_repo: FilmCacheRepository

    async def get_by_id(self, film_id: str) -> Film | None:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self.cache_repo.get(film_id=film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self.elastic_repo.get_by_id(film_id=film_id)
            if not film:
                # Если он отсутствует в Elasticsearch,
                # значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self.cache_repo.put(film=film)

        return film

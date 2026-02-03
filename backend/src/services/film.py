from uuid import UUID

from attrs import frozen
from models.film import Film
from repositories.cache.film_cache import FilmCacheRepository
from repositories.elastic.film_elastic import FilmElasticRepository

SORT_FIELDS = {
    "imdb_rating": "imdb_rating",
    "title": "title.raw",
    }


@frozen
class FilmService:
    elastic_repo: FilmElasticRepository
    cache_repo: FilmCacheRepository

    async def get_by_id(self, film_id: UUID) -> Film | None:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film_id_str = str(film_id)
        film = await self.cache_repo.get(film_id=film_id_str)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self.elastic_repo.get_by_id(film_id=film_id_str)
            if not film:
                # Если он отсутствует в Elasticsearch,
                # значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self.cache_repo.put(film=film)

        return film

    async def get_list(
        self,
        sort: str | None,
        genre: UUID | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:

        genre_str = str(genre)
        cache_key = self._build_cache_key(
            sort=sort,
            genre=genre_str,
            page=page,
            size=size,
            )
        cached = await self.cache_repo.get_list(cache_key)
        if cached:
            return cached

        sort_field = "imdb_rating"
        sort_order = "desc"

        if sort:
            sort_order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            sort_field = SORT_FIELDS.get(field, "imdb_rating")

        result = await self.elastic_repo.get_list(
            sort_field=sort_field,
            sort_order=sort_order,
            genre=genre_str,
            page=page,
            size=size,
            )
        await self.cache_repo.put_list(cache_key, result)

        return result

    async def search(
        self,
        query: str,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        return await self.elastic_repo.search(
            query=query,
            page=page,
            size=size,
            )

    async def get_by_person(
        self,
        person_id: UUID,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        person_id_str = str(person_id)
        return await self.elastic_repo.get_by_person_id(
            person_id=person_id_str,
            page=page,
            size=size,
            )

    def _build_cache_key(
        self,
        sort: str,
        genre: str,
        page: int,
        size: int,
        ) -> str:
        return (
            "films:list:"
            f"sort={sort or 'default'}:"
            f"genre={genre or 'all'}:"
            f"page={page}:"
            f"size={size}"
        )

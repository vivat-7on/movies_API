from uuid import UUID

from attrs import frozen
from elasticsearch import NotFoundError

from models.film import Film
from repositories.cache.film_cache import FilmCacheRepository
from repositories.elastic.film_elastic import FilmElasticRepository


@frozen
class FilmService:
    elastic_repo: FilmElasticRepository
    cache_repo: FilmCacheRepository

    async def get_by_id(self, film_id: UUID) -> Film | None:
        # Пытаемся получить данные из кеша
        film_id_str = str(film_id)
        film = await self.cache_repo.get(entity_id=film_id_str)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self.elastic_repo.get_by_id(entity_id=film_id_str)
            if not film:
                # Если он отсутствует в Elasticsearch,
                # значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм в кеш
            await self.cache_repo.put(data=film)

        return film

    async def get_list(
        self,
        sort: str | None,
        genre: UUID | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:

        cache_key = self._build_list_cache_key(
            sort=sort,
            genre=str(genre) if genre else None,
            page=page,
            size=size,
            )
        cached = await self.cache_repo.get_list(cache_key)
        if cached is not None:
            return cached

        result = await self.elastic_repo.get_films_list(
            sort=sort,
            genre=str(genre) if genre else None,
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

        cache_key = self._build_search_cache_key(
            query=query,
            page=page,
            size=size,
            )

        cached = await self.cache_repo.get_list(cache_key)

        if cached is not None:
            return cached

        try:
            result = await self.elastic_repo.search(
                text=query,
                page=page,
                size=size,
                )
        except NotFoundError:
            cached = await self.cache_repo.get_list(cache_key)
            if cached is not None:
                return cached
            raise

        await self.cache_repo.put_list(
            key=cache_key,
            value=result,
            ttl=60,
            )

        return result

    async def get_by_person(
        self,
        person_id: UUID,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        person_id_str = str(person_id)

        cache_key = self._build_person_cache_key(
            person_id=person_id_str,
            page=page,
            size=size,
            )

        cached = await self.cache_repo.get_list(cache_key)

        if cached is not None:
            return cached

        try:
            result = await self.elastic_repo.get_by_person_id(
                person_id=person_id_str,
                page=page,
                size=size,
                )
        except NotFoundError:
            cached = await self.cache_repo.get_list(cache_key)
            if cached is not None:
                return cached
            raise

        await self.cache_repo.put_list(cache_key, result)

        return result

    def _build_list_cache_key(
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

    def _build_search_cache_key(
        self,
        query: str,
        page: int,
        size: int,
        ) -> str:
        query = " ".join(query.strip().lower().split())
        return (
            "films:search:"
            f"query={query or 'default'}:"
            f"page={page}:"
            f"size={size}"
        )

    def _build_person_cache_key(
        self,
        person_id: str,
        page: int,
        size: int,
        ) -> str:
        return (
            "films:person:"
            f"person_id={person_id}:"
            f"page={page}:"
            f"size={size}"
        )

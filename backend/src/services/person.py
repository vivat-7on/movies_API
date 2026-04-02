from uuid import UUID

from attrs import frozen
from elasticsearch import NotFoundError

from models.film import Person, Film
from repositories.cache.person_cache import PersonCacheRepository
from repositories.elastic.person_elastic import PersonElasticRepository
from services.film import FilmService

SORT_FIELDS = {
    "name": "name.raw",
    }


@frozen
class PersonService:
    elastic_repo: PersonElasticRepository
    cache_repo: PersonCacheRepository
    film_service: FilmService

    async def get_by_id(self, person_id: UUID) -> Person | None:
        person_id_str = str(person_id)
        person = await self.cache_repo.get(entity_id=person_id_str)
        if not person:
            person = await self.elastic_repo.get_by_id(person_id=person_id_str)
            if not person:
                return None
            await self.cache_repo.put(data=person)

        return person

    async def get_list(
        self,
        sort: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Person]]:
        cache_key = self._build_cache_list_key(
            sort=sort,
            page=page,
            size=size,
            )
        cached = await self.cache_repo.get_list(cache_key)
        if cached:
            return cached

        sort_field = "name.raw"
        sort_order = "desc"

        if sort:
            sort_order = "desc" if sort.startswith("-") else "asc"
            field = sort.lstrip("-")
            sort_field = SORT_FIELDS.get(field, "name.raw")

        try:
            result = await self.elastic_repo.get_list(
                sort_field=sort_field,
                sort_order=sort_order,
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

    async def get_films(
        self,
        person_id: UUID,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        return await self.film_service.get_by_person(
            person_id=person_id,
            page=page,
            size=size,
            )

    async def search(
        self,
        query: str,
        page_number: int,
        page_size: int,
        ) -> tuple[int, list[Person]]:
        cache_key = self._build_search_cache_key(
            query=query,
            page=page_number,
            size=page_size,
            )

        cached = await self.cache_repo.get_list(cache_key)
        if cached is not None:
            return cached

        try:
            result = await self.elastic_repo.search(
                query=query,
                page_number=page_number,
                page_size=page_size,
                )
        except NotFoundError:
            cached = await self.cache_repo.get_list(cache_key)
            if cached is not None:
                return cached
            raise

        await self.cache_repo.put_list(key=cache_key, value=result)

        return result

    def _build_cache_list_key(
        self,
        sort: str,
        page: int,
        size: int,
        ) -> str:
        return (
            "person:list:"
            f"sort={sort or 'default'}:"
            f"page={page}:"
            f"size={size}"
        )

    def _build_search_cache_key(
        self,
        query: str,
        page: int,
        size: int,
        ) -> str:
        return (
            "person:search:"
            f"query={query or 'all'}:"
            f"page={page}:"
            f"size={size}"
        )

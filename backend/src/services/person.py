from attrs import frozen

from models.film import Person
from repositories.cache.person_cache import PersonCacheRepository
from repositories.elastic.person_elastic import PersonElasticRepository

SORT_FIELDS = {
    "name": "name.raw",
    }


@frozen
class PersonService:
    elastic_repo: PersonElasticRepository
    cache_repo: PersonCacheRepository

    async def get_by_id(self, person_id: str) -> Person | None:
        person = await self.cache_repo.get(person_id=person_id)
        if not person:
            person = await self.elastic_repo.get_by_id(person_id=person_id)
            if not person:
                return None
            await self.cache_repo.put(person=person)

        return person

    async def get_list(
        self,
        sort: str | None,
        page: int,
        size: int,
        search: str | None,
        ) -> tuple[int, list[Person]]:
        cache_key = self._build_cache_key(
            sort=sort,
            search=search,
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

        result = await self.elastic_repo.get_list(
            sort_field=sort_field,
            sort_order=sort_order,
            search=search,
            page=page,
            size=size,
            )
        await self.cache_repo.put_list(cache_key, result)

        return result

    def _build_cache_key(
        self,
        sort: str,
        search: str,
        page: int,
        size: int,
        ) -> str:
        return (
            "person:list:"
            f"sort={sort or 'default'}:"
            f"query={search or 'all'}:"
            f"page={page}:"
            f"size={size}"
        )

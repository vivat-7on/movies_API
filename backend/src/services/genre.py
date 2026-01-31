from attrs import frozen

from models.film import Genre
from repositories.cache.genre_cache import GenreCacheRepository
from repositories.elastic.genre_elastic import GenreElasticRepository

SORT_FIELDS = {
    "name": "name.raw",
    }


@frozen
class GenreService:
    elastic_repo: GenreElasticRepository
    cache_repo: GenreCacheRepository

    async def get_by_id(
        self,
        genre_id: str,
        ) -> Genre | None:
        genre = await self.cache_repo.get(genre_id=genre_id)
        if not genre:
            genre = await self.elastic_repo.get_by_id(genre_id=genre_id)
            if not genre:
                return None

            await self.cache_repo.put(genre=genre)

        return genre

    async def get_list(
        self,
        sort: str | None,
        search: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Genre]]:
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
            "genre:list:"
            f"sort={sort or 'default'}:"
            f"search={search or 'all'}:"
            f"page={page}:"
            f"size={size}"
        )

from attrs import frozen
from elasticsearch import NotFoundError
from models.film import Genre
from repositories.cache.genre_cache import GenreCacheRepository
from repositories.elastic.genre_elastic import GenreElasticRepository


@frozen
class GenreService:
    elastic_repo: GenreElasticRepository
    cache_repo: GenreCacheRepository

    async def get_by_id(
        self,
        genre_id: str,
    ) -> Genre | None:
        genre = await self.cache_repo.get(entity_id=genre_id)
        if not genre:
            genre = await self.elastic_repo.get_by_id(entity_id=genre_id)
            if not genre:
                return None

            await self.cache_repo.put(data=genre)

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

        try:
            result = await self.elastic_repo.get_genres_list(
                sort=sort,
                search=search,
                page=page,
                size=size,
            )
        except NotFoundError:
            cached = await self.cache_repo.get_list(cache_key)
            if cached:
                return cached
            raise

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

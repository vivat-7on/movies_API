from attrs import frozen
from models.film import Film
from repositories.film_cache import FilmCacheRepository
from repositories.film_elastic import FilmElasticRepository

SORT_FIELDS = {
    "imdb_rating": "imdb_rating",
    "title": "title.raw",
    }


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

    async def get_list(
        self,
        sort: str | None,
        genre: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:

        cache_key = self._build_cache_key(
            sort=sort,
            genre=genre,
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
            genre=genre,
            page=page,
            size=size,
            )
        await self.cache_repo.put_list(cache_key, result)

        return result

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

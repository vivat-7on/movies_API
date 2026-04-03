from elasticsearch import AsyncElasticsearch

from models.film import Film
from repositories.elastic.base import BaseElasticRepository
from repositories.elastic.query_builder import QueryBuilder
from repositories.elastic.sort_builder import SortBuilder

SORT_FIELDS = {
    "imdb_rating": "imdb_rating",
    "title": "title.raw",
    }


class FilmElasticRepository(BaseElasticRepository[Film]):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        super().__init__(
            elastic=elastic,
            index="movies",
            model=Film,
            )

    async def get_films_list(
        self,
        sort: str | None,
        genre: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        query_builder = QueryBuilder()

        if genre:
            query_builder.filter_nested(
                path="genres",
                field="genres.id",
                value=genre,
                )

        query = query_builder.build()

        field, order = self._parse_sort(sort)

        sort_clause = None

        if field and order:
            sort_builder = SortBuilder(set(SORT_FIELDS.values()))
            mapped_field = SORT_FIELDS.get(field)
            if mapped_field:
                sort_builder.add(
                    field=mapped_field,
                    order=order,
                    )
                sort_clause = sort_builder.build()

        return await super().get_list(
            query=query,
            page=page,
            size=size,
            sort=sort_clause,
            )

    async def search(
        self,
        text: str,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:

        search_query = {
            "multi_match": {
                "query": text,
                "fields": [
                    "title^3",
                    "description",
                    "actors_names",
                    "directors_names",
                    "writers_names",
                    ],
                },
            }

        return await super().get_list(
            query=search_query,
            page=page,
            size=size,
            sort=None,
            )

    async def get_by_person_id(
        self,
        person_id: str,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:

        query_builder = QueryBuilder()

        query_builder.should_nested(
            path="actors",
            field="actors.id",
            value=person_id,
            )
        query_builder.should_nested(
            path="directors",
            field="directors.id",
            value=person_id,
            )
        query_builder.should_nested(
            path="writers",
            field="writers.id",
            value=person_id,
            )
        query = query_builder.build()

        return await super().get_list(
            query=query,
            page=page,
            size=size,
            sort=None,
            )

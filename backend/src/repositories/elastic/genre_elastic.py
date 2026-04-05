from elasticsearch import AsyncElasticsearch
from models.film import Genre

from repositories.elastic.base import BaseElasticRepository
from repositories.elastic.query_builder import QueryBuilder
from repositories.elastic.sort_builder import SortBuilder

SORT_FIELDS = {
    "name": "name.raw",
}


class GenreElasticRepository(BaseElasticRepository[Genre]):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        super().__init__(
            elastic=elastic,
            index="genres",
            model=Genre,
        )

    async def get_genres_list(
        self,
        sort: str | None,
        search: str | None,
        page: int,
        size: int,
    ) -> tuple[int, list[Genre]]:
        query_builder = QueryBuilder()

        if search:
            query_builder.match(
                field="name",
                value=search,
                operator="and",
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

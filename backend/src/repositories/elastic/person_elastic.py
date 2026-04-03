from elasticsearch import AsyncElasticsearch

from models.film import Person
from repositories.elastic.base import BaseElasticRepository
from repositories.elastic.query_builder import QueryBuilder
from repositories.elastic.sort_builder import SortBuilder

SORT_FIELDS = {
    "name": "name.raw",
    }


class PersonElasticRepository(BaseElasticRepository[Person]):
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        super().__init__(
            elastic=elastic,
            index="persons",
            model=Person,
            )

    async def get_persons_list(
        self,
        sort: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Person]]:
        query = QueryBuilder().build()

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
        ) -> tuple[int, list[Person]]:

        query = {
            "multi_match": {
                "query": text,
                "fields": ["name"],
                "fuzziness": "AUTO",
                },
            }

        return await super().get_list(
            query=query,
            page=page,
            size=size,
            sort=None,
            )

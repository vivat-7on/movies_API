from typing import Generic, Type, TypeVar

from elasticsearch import AsyncElasticsearch, NotFoundError

T = TypeVar("T")


class BaseElasticRepository(Generic[T]):
    def __init__(
        self,
        elastic: AsyncElasticsearch,
        index: str,
        model: Type[T],
    ) -> None:
        self.elastic = elastic
        self.index = index
        self.model = model

    async def get_by_id(self, entity_id: str) -> T | None:
        try:
            doc = await self.elastic.get(index=self.index, id=entity_id)
        except NotFoundError:
            return None
        return self.model(**doc["_source"])

    async def get_list(
        self,
        query: dict,
        page: int,
        size: int,
        sort: list | None,
    ) -> tuple[int, list[T]]:
        offset = self._get_offset(page, size)

        params = {
            "index": self.index,
            "query": query,
            "from_": offset,
            "size": size,
        }

        if sort:
            params["sort"] = sort  # type: ignore

        try:
            response = await self.elastic.search(**params)
        except NotFoundError:
            return 0, []

        return self._parse_response(response)

    def _parse_response(self, response) -> tuple[int, list[T]]:
        hits = response.get("hits", {})
        total = hits.get("total", {}).get("value", 0)

        films = [self.model(**hit["_source"]) for hit in hits.get("hits", [])]
        return total, films

    def _get_offset(self, page: int, size: int) -> int:
        return (page - 1) * size

    @staticmethod
    def _parse_sort(sort: str | None) -> tuple[str | None, str | None]:
        if not sort:
            return None, None

        if sort.startswith("-"):
            return sort[1:], "desc"

        return sort, "asc"

from elasticsearch import AsyncElasticsearch, NotFoundError

from models.film import Film


class FilmElasticRepository:
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Film | None:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def get_list(
        self,
        sort_field: str | None,
        sort_order: str | None,
        genre: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        offset = (page - 1) * size

        query: dict = {"bool": {"filter": []}}
        if genre:
            query["bool"]["filter"].append(
                {"term": {"genres": genre}},
                )
        if not query["bool"]["filter"]:
            query = {"match_all": {}}

        body: dict = {
            "from": offset,
            "size": size,
            "query": query,
            "sort": [
                {
                    sort_field: {
                        "order": sort_order,
                        "missing": "_last",
                        },
                    }
                ],
            }

        response = await self.elastic.search(
            index="movies",
            body=body,
            )
        total = response["hits"]["total"]["value"]
        films = [
            Film(**hit["_source"])
            for hit in response["hits"]["hits"]
            ]
        return total, films

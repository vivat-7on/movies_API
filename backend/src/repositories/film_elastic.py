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
        page: int,
        size: int,
    ) -> tuple[int, list[Film]]:
        offset = (page - 1) * size

        query = {
           "query": {"match_all": {}},
            "from": offset,
            "size": size,
            "sort": [
                {"imdb_rating": {"order": "desc", "missing": "_last"}}
            ],
        }
        response = await self.elastic.search(
            index="movies",
            body=query,
        )
        total = response["hits"]["total"]["value"]
        films = [
            Film(**hit["_source"])
            for hit in response["hits"]["hits"]
        ]
        return total, films

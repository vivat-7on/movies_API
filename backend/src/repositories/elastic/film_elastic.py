from elasticsearch import AsyncElasticsearch, NotFoundError

from models.film import Film


class FilmElasticRepository:
    def __init__(self, elastic: AsyncElasticsearch) -> None:
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

        filters = []

        if genre:
            filters.append(
                {
                    "nested": {
                        "path": "genres",
                        "query": {
                            "term": {
                                "genres.id": genre,
                                },
                            },
                        },
                    },
                )

        query: dict
        if filters:
            query = {"bool": {"filter": filters}}
        else:
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
                    },
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

    async def search(
        self,
        query: str,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        offset = (page - 1) * size

        body: dict = {
            "from": offset,
            "size": size,
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "title^3",
                        "description",
                        "actors_names",
                        "directors_names",
                        "writers_names",
                        ],
                    },
                },
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

    async def get_by_person_id(
        self,
        person_id: str,
        page: int,
        size: int,
        ) -> tuple[int, list[Film]]:
        offset = (page - 1) * size

        body = {
            "from": offset,
            "size": size,
            "query": {
                "bool": {
                    "filter": [
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "term": {
                                        "actors.id": person_id,
                                        },
                                    },
                                },
                            },
                        ],
                    },
                },
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

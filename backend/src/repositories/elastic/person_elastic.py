from elasticsearch import AsyncElasticsearch, NotFoundError

from models.film import Person


class PersonElasticRepository:
    def __init__(self, elastic: AsyncElasticsearch) -> None:
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Person | None:
        try:
            doc = await self.elastic.get(index="persons", id=person_id)
        except NotFoundError:
            return None
        return Person(**doc["_source"])

    async def get_list(
        self,
        sort_field: str | None,
        sort_order: str | None,
        search: str | None,
        page: int,
        size: int,
        ) -> tuple[int, list[Person]]:
        offset = (page - 1) * size

        if search:
            query = {
                "match": {
                    "name": {
                        "query": search,
                        "operator": "and",
                        }
                    }
                }
        else:
            query = {"match_all": {}}

        body = {
            "from": offset,
            "size": size,
            "query": query,
            "sort": [
                {
                    sort_field: {
                        "order": sort_order,
                        "missing": "_last",
                        }
                    }
                ],
            }
        response = await self.elastic.search(
            index="persons",
            body=body,
            )

        total = response["hits"]["total"]["value"]
        persons = [
            Person(**hit["_source"])
            for hit in response["hits"]["hits"]
            ]

        return total, persons

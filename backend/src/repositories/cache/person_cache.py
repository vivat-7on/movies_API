import json

from redis.asyncio import Redis

from models.film import Person

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
LIST_PERSON_CACHE_EXPIRE_IN_SECONDS = 60  # 1 минута


class PersonCacheRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, person_id: str) -> Person | None:
        key = f"person:{person_id}"
        data = await self.redis.get(key)
        if not data:
            return None

        person = Person.model_validate_json(data)
        return person

    async def put(self, person: Person) -> None:
        await self.redis.set(
            f"person:{person.id}",
            person.model_dump_json(),
            PERSON_CACHE_EXPIRE_IN_SECONDS,
            )

    async def get_list(self, key: str) -> tuple[int, list[Person]] | None:
        data = await self.redis.get(key)
        if not data:
            return None

        obj = json.loads(data)
        total = obj["total"]
        persons = [Person(**person) for person in obj["persons"]]
        return total, persons

    async def put_list(self, key: str, value: tuple[int, list[Person]]) -> None:
        total, persons = value
        payload = {
            "total": total,
            "persons": [person.model_dump() for person in persons]
            }
        await self.redis.set(
            key,
            json.dumps(payload),
            LIST_PERSON_CACHE_EXPIRE_IN_SECONDS,
            )

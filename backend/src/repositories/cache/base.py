import json
from typing import TypeVar, Generic, Type

from redis.asyncio import Redis

T = TypeVar("T")
CACHE_TTL = 60 * 5  # 5 минут
LIST_CACHE_TTL = 60  # 1 минута


class BaseCacheRepository(Generic[T]):
    def __init__(
        self,
        redis: Redis,
        model: Type[T],
        key_prefix: str,
        id_field: str = "id",
        ) -> None:
        self.redis = redis
        self.model = model
        self.key_prefix = key_prefix
        self.id_field = id_field

    async def get(self, entity_id: str) -> T | None:
        key = f"{self.key_prefix}:{entity_id}"
        data = await self.redis.get(key)
        if data is None:
            return None

        if isinstance(data, bytes):
            data = data.decode()

        result = self.model.model_validate_json(data)
        return result

    async def put(self, data: T) -> None:
        entity_id = getattr(data, self.id_field, None)
        if entity_id is None:
            raise AttributeError(
                f"{self.model.__name__} has no field {self.id_field}",
                )
        await self.redis.set(
            f"{self.key_prefix}:{entity_id}",
            data.model_dump_json(),
            CACHE_TTL,
            )

    async def get_list(self, key: str) -> tuple[int, list[T]] | None:
        data = await self.redis.get(key)
        if data is None:
            return None

        if isinstance(data, bytes):
            data = data.decode()

        obj = json.loads(data)
        total = obj.get("total", 0)
        results = [self.model.model_validate(r) for r in obj.get("results", [])]
        return total, results

    async def put_list(
        self,
        key: str,
        value: tuple[int, list[T]],
        ttl: int = LIST_CACHE_TTL,
        ) -> None:
        total, results = value
        payload = {
            "total": total,
            "results": [r.model_dump() for r in results],
            }
        await self.redis.set(key, json.dumps(payload), ttl)

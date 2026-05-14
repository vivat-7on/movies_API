from typing import Protocol


class ICacheStateRepo(Protocol):
    async def set(self, key: str, value: str, ttl: int) -> None: ...

    async def get_delete(self, key: str) -> str | None: ...

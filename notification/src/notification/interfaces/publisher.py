import uuid
from typing import Protocol


class IRabbitPublisher(Protocol):
    async def publish(self, notification_id: uuid.UUID) -> None: ...

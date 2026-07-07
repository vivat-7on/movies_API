import uuid

from pydantic import BaseModel, Field


class UserRegisteredEvent(BaseModel):
    user_id: uuid.UUID
    payload: dict = Field(default_factory=dict)


class BroadcastEvent(BaseModel):
    user_ids: list[uuid.UUID]
    template_code: str
    payload: dict = Field(default_factory=dict)

import uuid

from pydantic import BaseModel, Field


class UserRegisteredEvent(BaseModel):
    user_id: uuid.UUID
    payload: dict = Field(default_factory=dict)

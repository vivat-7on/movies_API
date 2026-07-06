import uuid

from pydantic import BaseModel, Field


class UserRegisteredEvent(BaseModel):
    user_id: uuid.UUID
    template_code: str = Field(default="welcome")
    payload: dict = Field(default_factory=dict)

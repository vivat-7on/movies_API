import uuid

from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: uuid.UUID
    user_roles: list[str] = Field(default_factory=list)

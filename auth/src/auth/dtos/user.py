import uuid

from pydantic import BaseModel


class UserDetailsDTO(BaseModel):
    id: uuid.UUID
    login: str
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None

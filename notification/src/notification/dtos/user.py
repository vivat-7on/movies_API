import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class UserData:
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str

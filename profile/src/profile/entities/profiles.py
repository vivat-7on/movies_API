import datetime
import uuid
from dataclasses import dataclass


@dataclass(frozen=True)
class Profile:
    id: uuid.UUID
    user_id: uuid.UUID
    phone: str
    first_name: str
    middle_name: str | None
    last_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

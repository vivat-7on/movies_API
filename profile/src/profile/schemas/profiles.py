import datetime
import uuid

from pydantic import BaseModel, ConfigDict, model_validator


class ProfileCreate(BaseModel):
    phone: str
    first_name: str
    middle_name: str | None = None
    last_name: str


class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    phone: str
    first_name: str
    middle_name: str | None
    last_name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileUpdate(BaseModel):
    phone: str | None = None
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str | None = None

    @model_validator(mode="after")
    def validate_not_empty(self) -> "ProfileUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field is required")

        required_fields = {"phone", "first_name", "last_name"}
        for field in required_fields:
            if getattr(self, field) is None:
                raise ValueError(f"Field {field} is required")

        return self

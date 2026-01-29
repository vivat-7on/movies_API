import datetime
import uuid
from dataclasses import dataclass

@dataclass
class PersonDTO:
    id: uuid.UUID
    full_name: str
    role: str | None

@dataclass
class GenreDTO:
    id: uuid.UUID
    name: str

@dataclass
class FilmWorkDTO:
    id: uuid.UUID
    title: str
    rating: float | None
    description: str | None
    persons: list[PersonDTO]
    genres: list[GenreDTO]
    updated_at: datetime.datetime | None

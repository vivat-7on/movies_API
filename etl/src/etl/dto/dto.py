import datetime
import uuid
from dataclasses import dataclass

@dataclass
class PersonDTO:
    id: uuid.UUID
    full_name: str

@dataclass
class FilmPersonDTO:
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
    persons: list[FilmPersonDTO]
    genres: list[GenreDTO]
    updated_at: datetime.datetime | None

@dataclass
class MovieState:
    film_work_ts: datetime.datetime | None
    genre_ts: datetime.datetime | None
    person_ts: datetime.datetime | None
    genre_film_work_ts: datetime.datetime | None
    person_film_work_ts: datetime.datetime | None

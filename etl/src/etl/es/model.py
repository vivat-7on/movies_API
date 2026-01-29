import uuid

from pydantic import BaseModel

class EsPerson(BaseModel):
    id: uuid.UUID
    name: str


class FilmEsDocument(BaseModel):
    id: uuid.UUID
    imdb_rating: float | None
    genres: list[str]
    title: str
    description: str | None
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]
    directors: list[EsPerson]
    actors: list[EsPerson]
    writers: list[EsPerson]

from pydantic import BaseModel


class Persons(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    imdb_rating: float | None
    genres: list[str]

    title: str
    description: str | None

    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]

    directors: list[Persons]
    actors: list[Persons]
    writers: list[Persons]

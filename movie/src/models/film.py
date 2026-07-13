from pydantic import BaseModel


class Persons(BaseModel):
    id: str
    name: str


class Genre(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    imdb_rating: float | None
    genres: list[Genre]

    title: str
    description: str | None

    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]

    directors: list[Persons]
    actors: list[Persons]
    writers: list[Persons]


class Person(BaseModel):
    id: str
    name: str

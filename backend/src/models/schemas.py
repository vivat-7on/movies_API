from pydantic import BaseModel


class PersonsResponse(BaseModel):
    id: str
    name: str


class FilmResponse(BaseModel):
    id: str
    imdb_rating: float | None
    genres: list[str]

    title: str
    description: str | None

    directors: list[PersonsResponse]
    actors: list[PersonsResponse]
    writers: list[PersonsResponse]


class FilmShort(BaseModel):
    id: str
    imdb_rating: float
    title: str


class FilmListResponse(BaseModel):
    count: int
    page: int
    size: int
    results: list[FilmShort]

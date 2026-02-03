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
    uuid: str
    title: str
    imdb_rating: float


class FilmListResponse(BaseModel):
    count: int
    page: int
    size: int
    results: list[FilmShort]


class GenreResponse(BaseModel):
    uuid: str
    name: str


class PersonResponse(BaseModel):
    uuid: str
    name: str


class GenreListResponse(BaseModel):
    count: int
    page: int
    size: int
    results: list[GenreResponse]


class PersonListResponse(BaseModel):
    count: int
    page: int
    size: int
    results: list[PersonResponse]

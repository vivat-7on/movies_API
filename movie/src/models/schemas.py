from pydantic import BaseModel


class PersonsResponse(BaseModel):
    uuid: str
    name: str


class GenreResponse(BaseModel):
    uuid: str
    name: str


class FilmResponse(BaseModel):
    uuid: str
    imdb_rating: float | None
    genres: list[GenreResponse]

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
    page_number: int
    page_size: int
    results: list[FilmShort]


class PersonResponse(BaseModel):
    uuid: str
    name: str


class GenreListResponse(BaseModel):
    count: int
    page_number: int
    page_size: int
    results: list[GenreResponse]


class PersonListResponse(BaseModel):
    count: int
    page_number: int
    page_size: int
    results: list[PersonResponse]

from pydantic import BaseModel


class FilmResponse(BaseModel):
    id: str
    title: str

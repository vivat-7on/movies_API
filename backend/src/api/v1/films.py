from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str) -> Film:
    return Film(id='some_id', title='some_title')

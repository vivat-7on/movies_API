from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from api.v1.container import create_film_service
from models.schemas import FilmResponse
from services.film import FilmService

router = APIRouter()


@router.get('/{film_id}', response_model=FilmResponse)
async def film_details(
        film_id: str,
        service: FilmService = Depends(create_film_service),
) -> FilmResponse:
    film = await service.get_by_id(film_id=film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Film with id={film_id} not found")
    return FilmResponse(
        id=film.id,
        title=film.title,
    )

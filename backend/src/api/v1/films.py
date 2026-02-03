from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends

from api.v1.container import create_film_service
from models.schemas import (
    FilmShort,
    FilmResponse,
    GenreResponse,
    PersonsResponse,
    FilmListResponse,
    )
from services.film import FilmService

router = APIRouter()


@router.get('/search', response_model=FilmListResponse)
async def films_search(
    query: str = Query(..., min_length=1),
    page_size: int = Query(50, ge=1, le=100),
    page_number: int = Query(1, ge=1, le=100),
    service: FilmService = Depends(create_film_service),
    ) -> FilmListResponse:
    total, films = await service.search(
        query=query,
        page=page_number,
        size=page_size,
        )
    return FilmListResponse(
        count=total,
        page_number=page_number,
        page_size=page_size,
        results=[
            FilmShort(
                uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
                ) for film in films
            ],
        )


@router.get('/{film_id}', response_model=FilmResponse)
async def film_details(
    film_id: UUID,
    service: FilmService = Depends(create_film_service),
    ) -> FilmResponse:
    film = await service.get_by_id(film_id=film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f"Film with id={film_id} not found",
            )
    return FilmResponse(
        uuid=film.id,
        imdb_rating=film.imdb_rating,
        genres=[GenreResponse(uuid=g.id, name=g.name) for g in film.genres],
        title=film.title,
        description=film.description,
        directors=[
            PersonsResponse(uuid=d.id, name=d.name)
            for d in film.directors
            ],
        actors=[
            PersonsResponse(uuid=a.id, name=a.name)
            for a in film.directors
            ],
        writers=[
            PersonsResponse(uuid=w.id, name=w.name)
            for w in film.directors
            ],
        )


@router.get('/', response_model=FilmListResponse)
async def film_list(
    page_number: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: str | None = Query(None),
    genre: UUID | None = Query(None),
    service: FilmService = Depends(create_film_service),
    ) -> FilmListResponse:
    total, films = await service.get_list(
        sort=sort,
        genre=genre,
        page=page_number,
        size=page_size,
        )
    return FilmListResponse(
        count=total,
        page_number=page_number,
        page_size=page_size,
        results=[
            FilmShort(
                uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
                ) for film in films
            ],
        )

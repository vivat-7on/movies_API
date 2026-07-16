from http import HTTPStatus
from uuid import UUID

from core.auth import TokenData
from fastapi import APIRouter, Depends, HTTPException, Query
from models.schemas import (
    FilmListResponse,
    FilmResponse,
    FilmShort,
    GenreResponse,
    PersonsResponse,
)
from services.film import FilmService

from api.v1.container import create_film_service
from api.v1.dependencies.pagination import PaginationQuery
from api.v1.dependencies.user import require_roles
from api.v1.sorting import FilmSortOptions

router = APIRouter()


@router.get("/new", response_model=FilmListResponse)
async def film_new(
    pagination: PaginationQuery = Depends(),
    sort: FilmSortOptions | None = Query(None),
    genre: UUID | None = Query(None),
    service: FilmService = Depends(create_film_service),
    current_user: TokenData = Depends(require_roles(["subscriber"])),
) -> FilmListResponse:
    total, films = await service.get_new(
        sort=sort,
        genre=genre,
        page=pagination.page_number,
        size=pagination.page_size,
    )
    return FilmListResponse(
        count=total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        results=[
            FilmShort(
                uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating or 0.0,
            )
            for film in films
        ],
    )


@router.get("/search", response_model=FilmListResponse)
async def films_search(
    query: str = Query(..., min_length=1),
    pagination: PaginationQuery = Depends(),
    service: FilmService = Depends(create_film_service),
) -> FilmListResponse:
    total, films = await service.search(
        query=query,
        page=pagination.page_number,
        size=pagination.page_size,
    )
    return FilmListResponse(
        count=total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        results=[
            FilmShort(
                uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating or 0.0,
            )
            for film in films
        ],
    )


@router.get("/{film_id}", response_model=FilmResponse)
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
        directors=[PersonsResponse(uuid=d.id, name=d.name) for d in film.directors],
        actors=[PersonsResponse(uuid=a.id, name=a.name) for a in film.actors],
        writers=[PersonsResponse(uuid=w.id, name=w.name) for w in film.writers],
    )


@router.get("/", response_model=FilmListResponse)
async def film_list(
    pagination: PaginationQuery = Depends(),
    sort: FilmSortOptions | None = Query(None),
    genre: UUID | None = Query(None),
    service: FilmService = Depends(create_film_service),
) -> FilmListResponse:
    total, films = await service.get_list(
        sort=sort,
        genre=genre,
        page=pagination.page_number,
        size=pagination.page_size,
    )
    return FilmListResponse(
        count=total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        results=[
            FilmShort(
                uuid=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating or 0.0,
            )
            for film in films
        ],
    )

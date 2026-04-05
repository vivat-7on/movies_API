from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from models.schemas import GenreListResponse, GenreResponse
from services.genre import GenreService

from api.v1.container import create_genre_service
from api.v1.dependencies.pagination import PaginationQuery
from api.v1.sorting import GenreSortOptions

router = APIRouter()


@router.get("/{genre_id}", response_model=GenreResponse)
async def get_genre(
    genre_id: UUID,
    service: GenreService = Depends(create_genre_service),
) -> GenreResponse:
    genre = await service.get_by_id(genre_id=str(genre_id))
    if not genre:
        raise HTTPException(
            status_code=404,
            detail=f"Genre with id={genre_id} not found",
        )
    return GenreResponse(
        uuid=genre.id,
        name=genre.name,
    )


@router.get("/", response_model=GenreListResponse)
async def genres_list(
    pagination: PaginationQuery = Depends(),
    sort: GenreSortOptions | None = Query(None),
    search: str | None = Query(None),
    service: GenreService = Depends(create_genre_service),
) -> GenreListResponse:
    total, genres = await service.get_list(
        page=pagination.page_number,
        size=pagination.page_size,
        sort=sort,
        search=search,
    )
    return GenreListResponse(
        count=total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        results=[
            GenreResponse(
                uuid=genre.id,
                name=genre.name,
            )
            for genre in genres
        ],
    )

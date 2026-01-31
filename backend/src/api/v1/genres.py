from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.container import create_genre_service
from models.schemas import GenreResponse, GenreListResponse
from services.genre import GenreService

router = APIRouter()


@router.get("/{genre_id}", response_model=GenreResponse)
async def get_genre(
    genre_id: str,
    service: GenreService = Depends(create_genre_service),
    ) -> GenreResponse:
    genre = await service.get_by_id(genre_id=genre_id)
    if not genre:
        raise HTTPException(
            status_code=404,
            detail=f"Genre with id={genre_id} not found",
            )
    return GenreResponse(**genre.model_dump())


@router.get("/", response_model=GenreListResponse)
async def genres_list(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sort: str | None = Query(None),
    search: str | None = Query(None),
    service: GenreService = Depends(create_genre_service),
    ) -> GenreListResponse:
    total, genres = await service.get_list(
        page=page,
        size=size,
        sort=sort,
        search=search,
        )
    return GenreListResponse(
        count=total,
        page=page,
        size=size,
        results=[
            GenreResponse(
                id=genre.id,
                name=genre.name,
                ) for genre in genres
            ],
        )

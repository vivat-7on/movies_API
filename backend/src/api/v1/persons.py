from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from models.schemas import (
    FilmListResponse,
    FilmShort,
    PersonListResponse,
    PersonResponse,
)
from services.person import PersonService

from api.v1.container import create_person_service
from api.v1.dependencies.pagination import PaginationQuery
from api.v1.sorting import PersonSortOptions

router = APIRouter()


@router.get("/search", response_model=PersonListResponse)
async def persons_search(
    query: str = Query(..., min_length=1),
    pagination: PaginationQuery = Depends(),
    service: PersonService = Depends(create_person_service),
) -> PersonListResponse:
    total, persons = await service.search(
        query=query,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
    )
    return PersonListResponse(
        count=total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        results=[
            PersonResponse(
                uuid=person.id,
                name=person.name,
            )
            for person in persons
        ],
    )


@router.get("/{person_id}/film", response_model=FilmListResponse)
async def persons_film(
    person_id: UUID,
    pagination: PaginationQuery = Depends(),
    service: PersonService = Depends(create_person_service),
) -> FilmListResponse:
    person = await service.get_by_id(person_id=person_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail=f"Person with id {person_id} not found",
        )
    total, films = await service.get_films(
        person_id=person_id,
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


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: UUID,
    service: PersonService = Depends(create_person_service),
) -> PersonResponse:
    person = await service.get_by_id(person_id=person_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail=f"Person with id {person_id} not found",
        )
    return PersonResponse(
        uuid=person.id,
        name=person.name,
    )


@router.get("/", response_model=PersonListResponse)
async def persons_list(
    pagination: PaginationQuery = Depends(),
    sort: PersonSortOptions | None = Query(None),
    service: PersonService = Depends(create_person_service),
) -> PersonListResponse:
    total, persons = await service.get_list(
        page=pagination.page_number,
        size=pagination.page_size,
        sort=sort,
    )
    return PersonListResponse(
        count=total,
        page_number=pagination.page_number,
        page_size=pagination.page_size,
        results=[
            PersonResponse(
                uuid=person.id,
                name=person.name,
            )
            for person in persons
        ],
    )

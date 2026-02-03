from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from api.v1.container import create_person_service
from models.schemas import (
    PersonResponse, PersonListResponse, FilmListResponse,
    FilmShort,
    )
from services.person import PersonService

router = APIRouter()


@router.get("/search", response_model=PersonListResponse)
async def persons_search(
    query: str = Query(..., min_length=1),
    page_number: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    service: PersonService = Depends(create_person_service),
    ) -> PersonListResponse:
    total, persons = await service.search(
        query=query,
        page_number=page_number,
        page_size=page_size,
        )
    return PersonListResponse(
        count=total,
        page_number=page_number,
        page_size=page_size,
        results=[
            PersonResponse(
                uuid=person.id,
                name=person.name,
                ) for person in persons
            ],
        )


@router.get("/{person_id}/film", response_model=FilmListResponse)
async def persons_film(
    person_id: UUID,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
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
    page_number: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: str | None = Query(None),
    search: str | None = Query(None),
    service: PersonService = Depends(create_person_service),
    ) -> PersonListResponse:
    total, persons = await service.get_list(
        page=page_number,
        size=page_size,
        sort=sort,
        search=search,
        )
    return PersonListResponse(
        count=total,
        page_number=page_number,
        page_size=page_size,
        results=[
            PersonResponse(
                uuid=person.id,
                name=person.name,
                ) for person in persons
            ],
        )

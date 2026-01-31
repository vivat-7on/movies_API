from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query

from api.v1.container import create_person_service
from models.schemas import PersonResponse, PersonListResponse
from services.person import PersonService

router = APIRouter()


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: str,
    service: PersonService = Depends(create_person_service),
    ) -> PersonResponse:
    person = await service.get_by_id(person_id=person_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail=f"Person with id {person_id} not found",
            )
    return PersonResponse(**person.model_dump())


@router.get("/", response_model=PersonListResponse)
async def persons_list(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    sort: str | None = Query(None),
    search: str | None = Query(None),
    service: PersonService = Depends(create_person_service),
    ) -> PersonListResponse:
    total, persons = await service.get_list(
        page=page,
        size=size,
        sort=sort,
        search=search,
        )
    return PersonListResponse(
        count=total,
        page=page,
        size=size,
        results=[
            PersonResponse(
                id=person.id,
                name=person.name,
                ) for person in persons
            ],
        )

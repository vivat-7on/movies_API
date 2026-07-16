import uuid

from fastapi import APIRouter, Depends
from starlette import status

from profile_service.api.v1.dependencies.auth import get_user_id
from profile_service.api.v1.dependencies.services import create_profile_service
from profile_service.entities.profiles import Profile
from profile_service.schemas.profiles import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from profile_service.services.profiles import ProfileService

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ProfileResponse,
)
async def create_profile(
    data: ProfileCreate,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> Profile:
    profile = await service.create_profile(
        user_id=user_id,
        data=data,
    )

    return profile


@router.get("/me", response_model=ProfileResponse)
async def get_profile(
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> Profile:
    profile = await service.get_by_user_id(user_id=user_id)

    return profile


@router.patch("/me", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> Profile:
    profile = await service.update_profile(
        user_id=user_id,
        data=data,
    )

    return profile


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> None:
    await service.delete_profile(user_id=user_id)

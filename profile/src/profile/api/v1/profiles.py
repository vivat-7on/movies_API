import datetime
import uuid
from profile.api.v1.dependencies.auth import get_user_id
from profile.api.v1.dependencies.services import create_profile_service
from profile.entities.profiles import Profile
from profile.schemas.profiles import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from profile.services.profiles import ProfileService

from fastapi import APIRouter, Depends
from starlette import status

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


@router.get("", response_model=ProfileResponse)
async def get_profiles(
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> ProfileResponse:
    return ProfileResponse(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79999999999",
        first_name="Вован",
        middle_name="Иванович",
        last_name="Побрякушкин",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )


@router.patch("/me", response_model=ProfileResponse)
async def update_profile(
    data: ProfileUpdate,
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> ProfileResponse:
    return ProfileResponse(
        id=uuid.uuid4(),
        user_id=user_id,
        phone=data.phone or "",
        first_name=data.first_name or "",
        middle_name=data.middle_name or "",
        last_name=data.last_name or "",
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now(),
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(
    user_id: uuid.UUID = Depends(get_user_id),
    service: ProfileService = Depends(create_profile_service),
) -> None:
    return None

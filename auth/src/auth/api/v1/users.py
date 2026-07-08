import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from auth.api.v1.dependencies import create_user_service, require_roles
from auth.api.v1.schemas import UserDetailsResponse, UserRoleCreateResponse
from auth.dtos.token import UserDTO
from auth.services.user_service import UserService

router = APIRouter()


@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_201_CREATED)
async def assign_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    service: UserService = Depends(create_user_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> UserRoleCreateResponse:
    await service.assign_user_role(
        user_id=user_id,
        role_id=role_id,
    )
    return UserRoleCreateResponse(
        user_id=str(user_id),
        role_id=str(role_id),
    )


@router.delete(
    "/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    service: UserService = Depends(create_user_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> None:
    await service.remove_user_role(
        user_id=user_id,
        role_id=role_id,
    )


@router.get("/{user_id}", response_model=UserDetailsResponse)
async def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(create_user_service),
) -> UserDetailsResponse:
    user = await service.get_user_by_id(user_id=user_id)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return UserDetailsResponse(
        id=user.id,
        login=user.login,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
    )

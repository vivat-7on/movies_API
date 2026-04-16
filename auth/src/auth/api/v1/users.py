import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from auth.api.v1.dependencies import create_user_service, require_roles
from auth.api.v1.schemas import UserRoleCreateResponse
from auth.dtos.token import UserDTO
from auth.exceptions.role import RoleNotFound
from auth.exceptions.user import UserNotFound
from auth.services.user_service import UserService

router = APIRouter()


@router.post("/{user_id}/roles/{role_id}", status_code=status.HTTP_201_CREATED)
async def assign_user_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    service: UserService = Depends(create_user_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> UserRoleCreateResponse:
    try:
        await service.assign_user_role(
            user_id=user_id,
            role_id=role_id,
        )
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc
    except RoleNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        ) from exc
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
    try:
        await service.remove_user_role(
            user_id=user_id,
            role_id=role_id,
        )
    except UserNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc

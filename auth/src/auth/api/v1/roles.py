import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from auth.api.v1.dependencies import create_role_service, require_roles
from auth.api.v1.schemas import RoleCreateResponse, RoleRequest, RoleResponse
from auth.dtos.token import UserDTO
from auth.exceptions.role import RoleAlreadyExist, RoleNotFound
from auth.services.role_service import RoleService

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleRequest,
    service: RoleService = Depends(create_role_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> RoleCreateResponse:
    try:
        await service.create_role(data.role_name)
    except RoleAlreadyExist as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This role already exists.",
        ) from exc
    return RoleCreateResponse(role=data.role_name)


@router.get("/", response_model=RoleResponse)
async def get_roles(
    service: RoleService = Depends(create_role_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> RoleResponse:
    roles = await service.get_roles()
    return RoleResponse(roles=roles)


@router.patch("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_role(
    role_id: uuid.UUID,
    data: RoleRequest,
    service: RoleService = Depends(create_role_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> None:
    try:
        await service.update_role(role_id, data.role_name)
    except RoleNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found.",
        ) from exc
    except RoleAlreadyExist as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This role already exists.",
        ) from exc


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: uuid.UUID,
    service: RoleService = Depends(create_role_service),
    user: UserDTO = Depends(require_roles(["admin"])),
) -> None:
    try:
        await service.delete_role(role_id)
    except RoleNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found.",
        ) from exc

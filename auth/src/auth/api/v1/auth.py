import uuid

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from auth.api.v1.dependencies import (
    create_auth_service,
    get_current_user,
    require_roles,
)
from auth.api.v1.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRegistrationRequest,
    UserResponse,
)
from auth.dtos.token import UserDTO
from auth.exceptions.auth import InvalidCredentials
from auth.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    service: AuthService = Depends(create_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("User-Agent", None)
    try:
        tokens = await service.login(
            login=data.login,
            password=data.password,
            user_agent=user_agent,
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from exc
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    data: UserRegistrationRequest,
    service: AuthService = Depends(create_auth_service),
) -> None:
    try:
        await service.user_registration(
            login=data.login,
            password=data.password,
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login or email already in use",
        ) from exc
    return


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    data: RefreshTokenRequest,
    service: AuthService = Depends(create_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("User-Agent", None)
    try:
        tokens = await service.refresh_access_token(
            refresh_token=data.refresh_token,
            user_agent=user_agent,
        )
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from exc
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.get("/me", response_model=UserResponse)
async def me(
    user: UserDTO = Depends(get_current_user),
) -> UserResponse:
    return UserResponse(user_id=user.user_id, roles=user.roles)


@router.post("/logout")
async def logout(
    data: RefreshTokenRequest,
    service: AuthService = Depends(create_auth_service),
) -> None:
    try:
        await service.logout(refresh_token=data.refresh_token)
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from exc
    return None


@router.post("/logout/all")
async def logout_all(
    user: UserDTO = Depends(get_current_user),
    service: AuthService = Depends(create_auth_service),
) -> None:
    try:
        await service.logout_all(user_id=uuid.UUID(user.user_id))
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from exc
    return None


@router.get("/admin")
async def admin_panel(user: UserDTO = Depends(require_roles(["admin"]))):
    return {"message": "Welcome admin"}

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from starlette.requests import Request

from auth.api.v1.dependencies import create_auth_service
from auth.api.v1.schemas import (
    LoginRequest,
    TokenResponse,
    UserRegistrationRequest,
)
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


@router.post("/registration")
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

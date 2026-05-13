import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette import status
from starlette.requests import Request

from auth.api.v1.dependencies import (
    create_auth_service,
    create_oauth_state_service,
    get_current_user,
    get_yandex_auth_settings,
    require_roles,
)
from auth.api.v1.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRegistrationRequest,
    UserResponse,
)
from auth.core.config import YandexAuthSettings
from auth.dtos.token import UserDTO
from auth.services.auth_service import AuthService
from auth.services.state_service import OAuthStateService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    service: AuthService = Depends(create_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("User-Agent", None)

    tokens = await service.login(
        login=data.login,
        password=data.password,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    data: UserRegistrationRequest,
    service: AuthService = Depends(create_auth_service),
) -> None:
    await service.user_registration(
        login=data.login,
        password=data.password,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    data: RefreshTokenRequest,
    service: AuthService = Depends(create_auth_service),
) -> TokenResponse:
    user_agent = request.headers.get("User-Agent", None)
    tokens = await service.refresh_access_token(
        refresh_token=data.refresh_token,
        user_agent=user_agent,
    )
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
    user: UserDTO = Depends(get_current_user),
) -> None:
    await service.logout(
        refresh_token=data.refresh_token,
        user_id=user.user_id,
    )


@router.post("/logout/all")
async def logout_all(
    user: UserDTO = Depends(get_current_user),
    service: AuthService = Depends(create_auth_service),
) -> None:
    await service.logout_all(user_id=uuid.UUID(user.user_id))


@router.get("/admin")
async def admin_panel(user: UserDTO = Depends(require_roles(["admin"]))):
    return {"message": "Welcome admin"}


@router.get("/yandex/login")
async def yandex_login(
    settings: YandexAuthSettings = Depends(get_yandex_auth_settings),
    state_service: OAuthStateService = Depends(
        create_oauth_state_service,
    ),
) -> RedirectResponse:
    state = await state_service.create_state()
    params = {
        "response_type": "code",
        "client_id": settings.YANDEX_CLIENT_ID,
        "redirect_uri": settings.YANDEX_REDIRECT_URI,
        "state": state,
    }
    url = f"{settings.YANDEX_AUTHORIZE_URI}?{urlencode(params)}"
    return RedirectResponse(url=url)


@router.get("/yandex/callback", response_model=TokenResponse)
async def yandex_callback(
    request: Request,
    state: str,
    code: str,
    error: str | None = None,
    auth_service: AuthService = Depends(create_auth_service),
    state_service: OAuthStateService = Depends(
        create_oauth_state_service,
    ),
) -> TokenResponse:
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )
    await state_service.validate_state(state)
    user_agent = request.headers.get("User-Agent", None)
    tokens = await auth_service.login_with_yandex(
        code=code,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette import status
from starlette.requests import Request

from auth.api.v1.dependencies import (
    create_auth_service,
    create_oauth_provider_resolver,
    create_oauth_state_service,
    create_rate_limit_service,
    get_current_user,
)
from auth.api.v1.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserRegistrationRequest,
    UserResponse,
)
from auth.core.enums import OAuthProviderName
from auth.dtos.token import UserDTO
from auth.exceptions.auth import InvalidCredentials
from auth.services.auth_service import AuthService
from auth.services.oauth_resolver import OAuthProviderResolver
from auth.services.rate_limit import RateLimitService
from auth.services.state_service import OAuthStateService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    data: LoginRequest,
    service: AuthService = Depends(create_auth_service),
    rate_limit_service: RateLimitService = Depends(create_rate_limit_service),
) -> TokenResponse:
    user_agent = request.headers.get("User-Agent", None)
    client_ip = request.client.host

    await rate_limit_service.ensure_login_allowed(
        ip=client_ip,
        login=data.login,
    )
    try:
        tokens = await service.login(
            login=data.login,
            password=data.password,
            user_agent=user_agent,
        )
    except InvalidCredentials:
        await rate_limit_service.register_failed_login_attempt(
            ip=client_ip,
            login=data.login,
        )
        raise

    await rate_limit_service.reset_login_attempts(
        ip=client_ip,
        login=data.login,
    )

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/registration", status_code=status.HTTP_201_CREATED)
async def registration(
    request: Request,
    data: UserRegistrationRequest,
    service: AuthService = Depends(create_auth_service),
    rate_limit_service: RateLimitService = Depends(create_rate_limit_service),
) -> None:
    client_ip = request.client.host
    await rate_limit_service.check_registration_limit(client_ip)
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


@router.get("/provider/{provider_name}/login")
async def provider_login(
    provider_name: OAuthProviderName,
    state_service: OAuthStateService = Depends(
        create_oauth_state_service,
    ),
    resolver: OAuthProviderResolver = Depends(create_oauth_provider_resolver),
) -> RedirectResponse:
    state = await state_service.create_state()
    provider = resolver.get_provider(provider_name)
    url = provider.get_authorize_url(state=state)
    return RedirectResponse(url=url)


@router.get("/provider/{provider_name}/callback", response_model=TokenResponse)
async def provider_callback(
    request: Request,
    provider_name: OAuthProviderName,
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
    tokens = await auth_service.login_with_oauth_provider(
        provider_name=provider_name,
        code=code,
        user_agent=user_agent,
    )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

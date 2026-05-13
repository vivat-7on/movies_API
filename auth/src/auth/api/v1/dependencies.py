from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.cache.redis_client import get_redis
from auth.core.config import (
    AuthSettings,
    DBSettings,
    RedisSettings,
    YandexAuthSettings,
)
from auth.db.session import get_session
from auth.dtos.token import UserDTO
from auth.exceptions.auth import InvalidCredentials
from auth.repositories.cache.state import CacheStateRepo
from auth.repositories.db.refresh_token_repo import RefreshTokenRepo
from auth.repositories.db.roles_repo import RoleRepo
from auth.repositories.db.social_account_repo import SocialAccountRepo
from auth.repositories.db.user_repo import UserRepo
from auth.repositories.db.user_role_repo import UserRoleRepo
from auth.services.auth_service import AuthService
from auth.services.role_service import RoleService
from auth.services.state_service import OAuthStateService
from auth.services.token_service import TokenService
from auth.services.user_service import UserService
from auth.services.yandex import YandexClient


@lru_cache
def get_db_settings():
    return DBSettings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


def get_yandex_auth_settings() -> YandexAuthSettings:
    return YandexAuthSettings()


def get_redis_settings() -> RedisSettings:
    return RedisSettings()


def create_yandex_client(
    yandex_auth_settings=Depends(get_yandex_auth_settings),
) -> YandexClient:
    return YandexClient(yandex_auth_settings=yandex_auth_settings)


def create_social_account(
    session=Depends(get_session),
) -> SocialAccountRepo:
    return SocialAccountRepo(session=session)


def create_user_repo(
    session: AsyncSession = Depends(get_session),
) -> UserRepo:
    return UserRepo(session=session)


def create_refresh_token_repo(
    session: AsyncSession = Depends(get_session),
) -> RefreshTokenRepo:
    return RefreshTokenRepo(session=session)


def create_token_service(
    auth_settings: AuthSettings = Depends(get_auth_settings),
) -> TokenService:
    return TokenService(auth_settings=auth_settings)


def create_role_repo(
    session: AsyncSession = Depends(get_session),
) -> RoleRepo:
    return RoleRepo(session=session)


def create_user_role_repo(
    session: AsyncSession = Depends(get_session),
) -> UserRoleRepo:
    return UserRoleRepo(session=session)


def create_cache_state_repo(
    redis=Depends(get_redis),
) -> CacheStateRepo:
    return CacheStateRepo(redis=redis)


def create_auth_service(
    user_repo: UserRepo = Depends(create_user_repo),
    refresh_token_repo: RefreshTokenRepo = Depends(create_refresh_token_repo),
    token_service: TokenService = Depends(create_token_service),
    auth_settings: AuthSettings = Depends(get_auth_settings),
    role_repo: RoleRepo = Depends(create_role_repo),
    user_role_repo: UserRoleRepo = Depends(create_user_role_repo),
    yandex_client: YandexClient = Depends(create_yandex_client),
    social_account_repo: SocialAccountRepo = Depends(create_social_account),
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        token_service=token_service,
        auth_settings=auth_settings,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        yandex_client=yandex_client,
        social_account_repo=social_account_repo,
        session=session,
    )


def create_role_service(
    role_repo: RoleRepo = Depends(create_role_repo),
) -> RoleService:
    return RoleService(role_repo=role_repo)


def create_user_service(
    user_repo: UserRepo = Depends(create_user_repo),
    role_repo: RoleRepo = Depends(create_role_repo),
    user_role_repo: UserRoleRepo = Depends(create_user_role_repo),
    token_service: TokenService = Depends(create_token_service),
) -> UserService:
    return UserService(
        user_repo=user_repo,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        token_service=token_service,
    )


def create_oauth_state_service(
    cache: CacheStateRepo = Depends(create_cache_state_repo),
) -> OAuthStateService:
    return OAuthStateService(cache=cache)


security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: UserService = Depends(create_user_service),
) -> UserDTO:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        return await service.get_current_user(str(token))
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_roles(required_roles: list[str]):
    if not required_roles:
        raise ValueError("Required roles cannot be empty")

    async def dependency(user: UserDTO = Depends(get_current_user)):
        user_roles = user.roles or []
        if not set(required_roles).intersection(user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return dependency

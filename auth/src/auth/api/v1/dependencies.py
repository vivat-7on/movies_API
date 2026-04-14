from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)
from starlette import status

from auth.core.config import AuthSettings, DBSettings
from auth.db.session import get_session
from auth.dtos.token import UserDTO
from auth.exceptions.auth import InvalidCredentials
from auth.repositories.refresh_token_repo import RefreshTokenRepo
from auth.repositories.roles_repo import RoleRepo
from auth.repositories.user_repo import UserRepo
from auth.repositories.user_role_repo import UserRoleRepo
from auth.services.auth_service import AuthService
from auth.services.token_service import TokenService


@lru_cache
def get_db_settings():
    return DBSettings()


@lru_cache
def get_auth_settings() -> AuthSettings:
    return AuthSettings()


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


def create_user_role_repo(
    session: AsyncSession = Depends(get_session),
) -> UserRoleRepo:
    return UserRoleRepo(session=session)


def create_role_repo(
    session: AsyncSession = Depends(get_session),
) -> RoleRepo:
    return RoleRepo(session=session)


def create_auth_service(
    user_repo: UserRepo = Depends(create_user_repo),
    refresh_token_repo: RefreshTokenRepo = Depends(create_refresh_token_repo),
    token_service: TokenService = Depends(create_token_service),
    auth_settings: AuthSettings = Depends(get_auth_settings),
    role_repo: RoleRepo = Depends(create_role_repo),
    user_role_repo: UserRoleRepo = Depends(create_user_role_repo),
    session: AsyncSession = Depends(get_session),
) -> AuthService:
    return AuthService(
        user_repo=user_repo,
        refresh_token_repo=refresh_token_repo,
        token_service=token_service,
        auth_settings=auth_settings,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        session=session,
    )


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(create_auth_service),
) -> UserDTO:
    token = credentials.credentials
    try:
        user = await service.get_current_user(token)
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
        ) from exc
    return user


def require_roles(required_roles: list[str]):
    async def dependency(user: UserDTO = Depends(get_current_user)):
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return dependency

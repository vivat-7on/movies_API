import uuid
from typing import Any, NoReturn

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from profile_service.core.config import AuthSettings, get_auth_settings

security = HTTPBearer(auto_error=False)

AUTH_HEADERS_NAME = "WWW-Authenticate"
AUTH_SCHEME = "Bearer"


def get_auth_headers() -> dict[str, str]:
    return {AUTH_HEADERS_NAME: AUTH_SCHEME}


def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers=get_auth_headers(),
    )


def verify_jwt_token(
    token: str,
    auth_settings: AuthSettings,
) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            auth_settings.jwt_public_key_path,
            algorithms=[auth_settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


def parse_user_id(payload: dict[str, Any]) -> uuid.UUID:
    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise_unauthorized(detail="Invalid token subject")

    try:
        return uuid.UUID(subject)
    except ValueError:
        raise_unauthorized("Invalid token subject")


async def get_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    auth_settings: AuthSettings = Depends(get_auth_settings),
) -> uuid.UUID:
    if credentials is None:
        raise_unauthorized(detail="Not authenticated")

    payload: dict[str, Any] | None = verify_jwt_token(
        token=credentials.credentials,
        auth_settings=auth_settings,
    )

    if payload is None:
        raise_unauthorized(detail="Invalid or expired token")

    return parse_user_id(payload)

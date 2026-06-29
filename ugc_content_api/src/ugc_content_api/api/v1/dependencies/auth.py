import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from ugc_content_api.core.settings import AuthSettings, get_auth_settings
from ugc_content_api.schemas.users import User

security = HTTPBearer()


def verify_jwt_token(
    token: str,
    auth_settings: AuthSettings,
) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            auth_settings.JWT_SECRET_KEY,
            algorithms=[auth_settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_settings: AuthSettings = Depends(get_auth_settings),
) -> User:
    token = credentials.credentials
    payload = verify_jwt_token(
        token=token,
        auth_settings=auth_settings,
    )
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    roles = payload.get("roles") or []
    if not isinstance(roles, list):
        roles = []

    user = User(
        user_id=uuid.UUID(user_id),
        user_roles=roles,
    )
    return user


def get_user_id(
    user: User = Depends(get_current_user),
) -> uuid.UUID:
    return user.user_id

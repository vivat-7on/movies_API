from core import config
from core.auth import TokenData, decode_token
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    token = credentials.credentials

    return decode_token(
        token=token,
        secret=config.JWT_PUBLIC_KEY_PATH,
        algorithm=config.JWT_ALGORITHM,
    )


def require_roles(required_roles: list[str]):
    def wrapper(user: TokenData = Depends(get_current_user)):
        if not user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No roles",
            )
        if not any(role in user.roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return user

    return wrapper

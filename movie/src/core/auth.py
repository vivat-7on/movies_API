from fastapi import HTTPException
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette import status


class TokenData(BaseModel):
    sub: str
    roles: list[str] = []
    token_version: int


def decode_token(token: str, secret: str, algorithm: str) -> TokenData:
    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return TokenData(**payload)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

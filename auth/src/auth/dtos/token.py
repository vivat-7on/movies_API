from pydantic import BaseModel


class ClaimDTO(BaseModel):
    sub: str
    roles: list[str]
    token_version: int
    iat: int
    exp: int


class TokensDTO(BaseModel):
    access_token: str
    refresh_token: str

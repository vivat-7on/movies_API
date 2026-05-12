from pydantic import BaseModel, Field


class ClaimDTO(BaseModel):
    sub: str
    roles: list[str]
    token_version: int
    iat: int
    exp: int


class TokensDTO(BaseModel):
    access_token: str
    refresh_token: str


class UserDTO(BaseModel):
    user_id: str
    roles: list[str]


class YandexTokensDTO(BaseModel):
    access_token: str
    expires_in: int | None = None
    refresh_token: str | None = None
    token_type: str


class YandexUserInfoDTO(BaseModel):
    id: str
    login: str | None = None
    client_id: str | None = None
    display_name: str | None = None
    real_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    sex: str | None = None
    default_email: str | None = None
    emails: list[str] = Field(default_factory=list)
    psuid: str | None = None

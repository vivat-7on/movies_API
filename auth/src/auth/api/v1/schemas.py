from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин, от 3 до 50 знаков",
    )
    password: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Пароль, от 5 до 50 знаков",
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserRegistrationRequest(BaseModel):
    login: str
    password: str
    email: str | None
    first_name: str | None
    last_name: str | None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    user_id: str
    roles: list[str]


class RoleRequest(BaseModel):
    role_name: str


class RoleResponse(BaseModel):
    roles: list[str]


class RoleCreateResponse(BaseModel):
    role: str

import uuid

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин, от 3 до 50 знаков",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль, от 8 до 128 знаков",
    )


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class UserRegistrationRequest(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин, от 3 до 50 знаков",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Пароль, от 8 до 128 знаков",
    )
    email: EmailStr | None = Field(default=None, description="Email пользователя")
    first_name: str | None = Field(
        default=None,
        max_length=50,
        description="Имя",
    )
    last_name: str | None = Field(
        default=None,
        max_length=50,
        description="Фамилия",
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=10)


class UserResponse(BaseModel):
    user_id: str
    roles: list[str]


class RoleRequest(BaseModel):
    role_name: str = Field(..., min_length=2, max_length=50)


class RoleResponse(BaseModel):
    roles: list[str]


class RoleCreateResponse(BaseModel):
    role: str


class UserRoleCreateResponse(BaseModel):
    user_id: str
    role_id: str


class UserDetailsResponse(BaseModel):
    id: uuid.UUID
    login: str
    email: EmailStr | None
    first_name: str | None
    last_name: str | None

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from auth.exceptions.auth import (
    EmailAlreadyExists,
    InvalidCredentials,
    LoginAlreadyExists,
)
from auth.exceptions.role import RoleAlreadyExist, RoleNotFound
from auth.exceptions.user import UserNotFound


def build_response(status_code: int, detail: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidCredentials)
    async def invalid_credentials_handler(
        request: Request,
        exc: InvalidCredentials,
    ):
        return build_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    @app.exception_handler(LoginAlreadyExists)
    async def login_already_exists_handler(
        request: Request,
        exc: LoginAlreadyExists,
    ):
        return build_response(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already exists",
        )

    @app.exception_handler(EmailAlreadyExists)
    async def email_already_exists_handler(
        request: Request,
        exc: EmailAlreadyExists,
    ):
        return build_response(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
        )

    @app.exception_handler(RoleAlreadyExist)
    async def role_already_exists_handler(
        request: Request,
        exc: RoleAlreadyExist,
    ):
        return build_response(
            status_code=status.HTTP_409_CONFLICT,
            detail="Role already exists",
        )

    @app.exception_handler(RoleNotFound)
    async def role_not_found_handler(
        request: Request,
        exc: RoleNotFound,
    ):
        return build_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )

    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFound,
    ):
        return build_response(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

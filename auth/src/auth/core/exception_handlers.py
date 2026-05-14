from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from auth.exceptions.auth import (
    EmailAlreadyExists,
    InvalidCredentials,
    LoginAlreadyExists,
)
from auth.exceptions.oauth import (
    InvalidOAuthState,
    LinkedOAuthUserNotFound,
    OAuthProviderNotSupported,
    OAuthTokenExchangeFailed,
    OAuthUserInfoFailed,
)
from auth.exceptions.rate_limit import TooManyRequests
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

    @app.exception_handler(InvalidOAuthState)
    async def invalid_oauth_state_handler(
        request: Request,
        exc: InvalidOAuthState,
    ):
        return build_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state",
        )

    @app.exception_handler(OAuthTokenExchangeFailed)
    async def yandex_token_exchange_failed_handler(
        request: Request,
        exc: OAuthTokenExchangeFailed,
    ):
        return build_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yandex token exchange failed",
        )

    @app.exception_handler(OAuthUserInfoFailed)
    async def yandex_user_info_failed_handler(
        request: Request,
        exc: OAuthUserInfoFailed,
    ):
        return build_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Yandex user info failed",
        )

    @app.exception_handler(LinkedOAuthUserNotFound)
    async def linked_yandex_user_not_found_handler(
        request: Request,
        exc: LinkedOAuthUserNotFound,
    ):
        return build_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Linked Yandex user not found",
        )

    @app.exception_handler(OAuthProviderNotSupported)
    async def yandex_providers_not_supported_handler(
        request: Request,
        exc: OAuthProviderNotSupported,
    ):
        return build_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider not supported",
        )

    @app.exception_handler(TooManyRequests)
    async def too_many_requests_handler(
        request: Request,
        exc: TooManyRequests,
    ):
        return build_response(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )

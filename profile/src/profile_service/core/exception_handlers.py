from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from profile_service.core.exceptions import DomainError


async def domain_error_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    if not isinstance(exc, DomainError):
        raise exc

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc)},
    )


def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        DomainError,
        domain_error_handler,
    )

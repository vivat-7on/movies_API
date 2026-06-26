from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from ugc_content_api.exceptions.base import DomainError


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request,
        exc: DomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc)},
        )

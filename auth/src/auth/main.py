import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from redis.asyncio import Redis

from auth.api.v1 import auth, roles, users
from auth.api.v1.dependencies import get_redis_settings
from auth.cache.redis_client import reset_redis_client, set_redis_client
from auth.core.exception_handlers import setup_exception_handlers

DEBUG = os.getenv("DEBUG", "true").lower() == "true"


def configure_tracer() -> None:
    resource = Resource.create({"service.name": "auth-service"})

    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTLP_ENDPOINT", "http://jaeger:4317"),
        insecure=True,
    )
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


configure_tracer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_settings = get_redis_settings()
    redis = Redis(
        host=redis_settings.REDIS_HOST,
        port=redis_settings.REDIS_PORT,
        decode_responses=True,
    )
    await redis.ping()
    set_redis_client(redis)

    yield
    await redis.close()
    reset_redis_client()


app = FastAPI(
    docs_url="/auth/docs" if DEBUG else None,
    openapi_url="/auth/openapi.json" if DEBUG else None,
    lifespan=lifespan,
)

FastAPIInstrumentor().instrument_app(app)


@app.middleware("http")
async def before_request(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        return ORJSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Missing X-Request-Id"},
        )
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


@app.get("/health")
async def health():
    return {"status": "ok"}


setup_exception_handlers(app)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])

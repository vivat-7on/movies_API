import os
import uuid
from pathlib import Path
from typing import AsyncGenerator, AsyncIterator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from jose import jwt
from profile_service.api.v1.dependencies.auth import get_auth_settings, get_user_id
from profile_service.api.v1.dependencies.services import create_profile_service
from profile_service.core.config import AuthSettings
from profile_service.db.tables import BaseTable
from profile_service.main import app
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

TEST_BASE_URL = "http://test"


@pytest.fixture
def user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def profile_service_mock() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
async def client(
    user_id: uuid.UUID,
    profile_service_mock: AsyncMock,
    auth_settings: AuthSettings,
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_user_id] = lambda: user_id
    app.dependency_overrides[get_auth_settings] = lambda: auth_settings
    app.dependency_overrides[create_profile_service] = lambda: profile_service_mock
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url=TEST_BASE_URL,
        ) as async_client:
            yield async_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def client_without_jwt(
    profile_service_mock: AsyncMock,
    auth_settings: AuthSettings,
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_auth_settings] = lambda: auth_settings
    app.dependency_overrides[create_profile_service] = lambda: profile_service_mock
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as async_client:
            yield async_client
    finally:
        app.dependency_overrides.clear()


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://profile_test:profile_test@localhost:5433/profile_test",
)


@pytest.fixture
async def integration_engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )
    async with engine.begin() as connection:
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS profile"))
        await connection.run_sync(BaseTable.metadata.create_all)
    try:
        yield engine
    finally:
        async with engine.begin() as connection:
            await connection.run_sync(BaseTable.metadata.drop_all)
            await connection.execute(
                text("DROP SCHEMA IF EXISTS profile CASCADE"),
            )

        await engine.dispose()


@pytest.fixture
async def integration_session(
    integration_engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    connection = await integration_engine.connect()
    transaction = await connection.begin()

    session_factory = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    try:
        async with session_factory() as session:
            yield session
    finally:
        if transaction.is_active:
            await transaction.rollback()
        await connection.close()


@pytest.fixture
def jwt_private_key_path() -> Path:
    return Path(__file__).parent / "keys" / "private.pem"


@pytest.fixture
def jwt_public_key_path() -> Path:
    return Path(__file__).parent / "keys" / "public.pem"


@pytest.fixture
def auth_settings(jwt_public_key_path: Path) -> AuthSettings:
    keys_dir = Path(__file__).parent / "keys"

    return AuthSettings(
        JWT_PUBLIC_KEY_PATH=keys_dir / "public.pem",
        JWT_ALGORITHM="RS256",
    )


@pytest.fixture
def access_token(
    user_id: uuid.UUID,
    jwt_private_key_path: Path,
) -> str:
    private_key = jwt_private_key_path.read_text(encoding="utf-8")

    return jwt.encode(
        {"sub": str(user_id)},
        private_key,
        algorithm="RS256",
    )


@pytest.fixture
async def client_with_real_jwt(
    access_token: str,
    auth_settings: AuthSettings,
    profile_service_mock: AsyncMock,
) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_auth_settings] = lambda: auth_settings
    app.dependency_overrides[create_profile_service] = lambda: profile_service_mock
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        ) as client:
            yield client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
async def client_with_invalid_jwt(
    profile_service_mock: AsyncMock,
    auth_settings: AuthSettings,
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_auth_settings] = lambda: auth_settings
    app.dependency_overrides[create_profile_service] = lambda: profile_service_mock

    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"Authorization": "Bearer invalid"},
        ) as async_client:
            yield async_client
    finally:
        app.dependency_overrides.clear()

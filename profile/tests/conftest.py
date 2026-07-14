import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from profile_service.api.v1.dependencies.auth import get_user_id
from profile_service.api.v1.profiles import create_profile_service
from profile_service.main import app


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
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_user_id] = lambda: user_id
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


@pytest.fixture
async def client_without_jwt(
    profile_service_mock: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
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

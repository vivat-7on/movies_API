import uuid
from unittest.mock import AsyncMock, Mock, patch

import pytest
from notification.core.auth_settings import AuthSettings
from notification.services.auth_client import AuthClient


@pytest.mark.asyncio
async def test_get_user_by_id_returns_user_data():
    user_id = uuid.uuid4()

    response = Mock()
    response.json.return_value = {
        "email": "user@test.com",
        "first_name": "Valerii",
        "last_name": "Semenov",
    }

    response.raise_for_status = Mock()

    client = AsyncMock()
    client.get.return_value = response

    with patch(
        "notification.services.auth_client.httpx.AsyncClient",
    ) as client_cls:
        client_cls.return_value.__aenter__.return_value = client

        auth_client = AuthClient(
            auth_settings=AuthSettings(
                AUTH_BASE_URL="https://auth:8000/api/v1",
                AUTH_USER_URL="/users/{user_id}",
            ),
        )
        result = await auth_client.get_user_by_id(user_id)

    assert result.id == user_id
    assert result.email == "user@test.com"
    assert result.first_name == "Valerii"
    assert result.last_name == "Semenov"

    client.get.assert_awaited_once()
    response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_id_uses_login_as_first_name_fallback():
    user_id = uuid.uuid4()

    response = Mock()
    response.json.return_value = {
        "email": "user@test.com",
        "login": "vivat",
        "last_name": "",
    }

    client = AsyncMock()
    client.get.return_value = response

    with patch(
        "notification.services.auth_client.httpx.AsyncClient",
    ) as client_cls:
        client_cls.return_value.__aenter__.return_value = client

        auth_client = AuthClient(
            auth_settings=AuthSettings(
                AUTH_BASE_URL="https://auth:8000/api/v1",
                AUTH_USER_URL="/users/{user_id}",
            ),
        )
        result = await auth_client.get_user_by_id(user_id)

    assert result.first_name == "vivat"

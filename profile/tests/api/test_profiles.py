import datetime
import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from profile_service.core.exceptions import (
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from profile_service.entities.profiles import Profile


@pytest.mark.asyncio
async def test_create_profile(
    client: AsyncClient,
    profile_service_mock,
    user_id: uuid.UUID,
) -> None:
    now = datetime.datetime.now(datetime.UTC)

    profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79998887766",
        first_name="John",
        middle_name=None,
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    profile_service_mock.create_profile.return_value = profile

    response = await client.post(
        "/api/v1/profiles",
        json={
            "phone": "8 999-888-77-66",
            "first_name": "John",
            "middle_name": None,
            "last_name": "Doe",
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": str(profile.id),
        "user_id": str(user_id),
        "phone": "+79998887766",
        "first_name": "John",
        "middle_name": None,
        "last_name": "Doe",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "updated_at": now.isoformat().replace("+00:00", "Z"),
    }

    profile_service_mock.create_profile.assert_awaited_once()

    call = profile_service_mock.create_profile.await_args
    assert call.kwargs["user_id"] == user_id
    assert call.kwargs["data"].phone == "8 999-888-77-66"


@pytest.mark.asyncio
async def test_create_profile_when_profile_exists(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    profile_service_mock.create_profile.side_effect = ProfileAlreadyExistsError()

    response = await client.post(
        "/api/v1/profiles",
        json={
            "phone": "8 999-888-77-66",
            "first_name": "John",
            "middle_name": None,
            "last_name": "Doe",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Profile already exists",
    }

    profile_service_mock.create_profile.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_profile_when_phone_exists(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    profile_service_mock.create_profile.side_effect = PhoneAlreadyExistsError()

    response = await client.post(
        "/api/v1/profiles",
        json={
            "phone": "8 999-888-77-66",
            "first_name": "John",
            "middle_name": None,
            "last_name": "Doe",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Phone already exists",
    }

    profile_service_mock.create_profile.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_profile_invalid_body(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    response = await client.post(
        "/api/v1/profiles",
        json={},
    )
    assert response.status_code == 422
    profile_service_mock.create_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_profile_without_jwt(
    client_without_jwt: AsyncClient,
    profile_service_mock,
) -> None:
    response = await client_without_jwt.post(
        "/api/v1/profiles",
        json={
            "phone": "8 999-888-77-66",
            "first_name": "John",
            "middle_name": None,
            "last_name": "Doe",
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated",
    }
    profile_service_mock.create_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_profile(
    client: AsyncClient,
    profile_service_mock,
    user_id: uuid.UUID,
) -> None:
    now = datetime.datetime.now(datetime.UTC)

    profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79998887766",
        first_name="John",
        middle_name=None,
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    profile_service_mock.get_by_user_id.return_value = profile

    response = await client.get("/api/v1/profiles/me")

    assert response.status_code == 200
    assert response.json() == {
        "id": str(profile.id),
        "user_id": str(user_id),
        "phone": "+79998887766",
        "first_name": "John",
        "middle_name": None,
        "last_name": "Doe",
        "created_at": now.isoformat().replace("+00:00", "Z"),
        "updated_at": now.isoformat().replace("+00:00", "Z"),
    }

    profile_service_mock.get_by_user_id.assert_awaited_once_with(
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_get_profile_not_found(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    profile_service_mock.get_by_user_id.side_effect = ProfileNotFoundError()

    response = await client.get("/api/v1/profiles/me")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Profile not found",
    }
    profile_service_mock.get_by_user_id.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_without_jwt(
    client_without_jwt: AsyncClient,
    profile_service_mock,
) -> None:
    response = await client_without_jwt.get("/api/v1/profiles/me")
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated",
    }
    profile_service_mock.get_by_user_id.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_profile(
    client: AsyncClient,
    profile_service_mock,
    user_id: uuid.UUID,
) -> None:
    now = datetime.datetime.now(datetime.UTC)

    profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79998887766",
        first_name="John",
        middle_name="Test",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    profile_service_mock.update_profile.return_value = profile

    response = await client.patch(
        "/api/v1/profiles/me",
        json={
            "phone": "8 999-888-77-66",
        },
    )

    assert response.status_code == 200
    assert response.json()["phone"] == "+79998887766"
    profile_service_mock.update_profile.assert_awaited_once()

    call = profile_service_mock.update_profile.await_args

    assert call.kwargs["user_id"] == user_id
    assert call.kwargs["data"].phone == "8 999-888-77-66"
    assert call.kwargs["data"].model_fields_set == {"phone"}


@pytest.mark.asyncio
async def test_update_profile_not_found(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    profile_service_mock.update_profile.side_effect = ProfileNotFoundError()

    response = await client.patch(
        "/api/v1/profiles/me",
        json={
            "phone": "8 999-888-77-66",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Profile not found",
    }


@pytest.mark.asyncio
async def test_update_profile_phone_exists(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    profile_service_mock.update_profile.side_effect = PhoneAlreadyExistsError()

    response = await client.patch(
        "/api/v1/profiles/me",
        json={
            "phone": "8 999-888-77-66",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": "Phone already exists",
    }


@pytest.mark.asyncio
async def test_update_empty(
    client: AsyncClient,
    profile_service_mock,
) -> None:
    response = await client.patch("/api/v1/profiles/me", json={})
    assert response.status_code == 422
    profile_service_mock.update_profile.assert_not_awaited()


@pytest.mark.parametrize(
    "field_name",
    [
        "phone",
        "first_name",
        "last_name",
    ],
)
@pytest.mark.asyncio
async def test_update_required_field_null(
    client: AsyncClient,
    profile_service_mock,
    field_name: str,
) -> None:
    response = await client.patch(
        "/api/v1/profiles/me",
        json={field_name: None},
    )

    assert response.status_code == 422
    profile_service_mock.update_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_without_jwt(
    client_without_jwt: AsyncClient,
    profile_service_mock,
) -> None:
    response = await client_without_jwt.patch(
        "/api/v1/profiles/me",
        json={
            "phone": "8 999-888-77-66",
        },
    )

    assert response.status_code == 401
    profile_service_mock.update_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_profile(
    client: AsyncClient,
    profile_service_mock,
    user_id: uuid.UUID,
) -> None:
    response = await client.delete("/api/v1/profiles/me")
    assert response.status_code == 204
    assert response.content == b""
    profile_service_mock.delete_profile.assert_awaited_once_with(
        user_id=user_id,
    )


@pytest.mark.asyncio
async def test_delete_profile_without_jwt(
    client_without_jwt: AsyncClient,
    profile_service_mock,
) -> None:
    response = await client_without_jwt.delete("/api/v1/profiles/me")
    assert response.status_code == 401
    assert response.json() == {
        "detail": "Not authenticated",
    }
    profile_service_mock.delete_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_profile_with_real_jwt(
    client_with_real_jwt: AsyncClient,
    profile_service_mock: AsyncMock,
    user_id: uuid.UUID,
) -> None:
    now = datetime.datetime.now(datetime.UTC)

    profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79998887766",
        first_name="John",
        middle_name="Test",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )
    profile_service_mock.create_profile.return_value = profile

    response = await client_with_real_jwt.post(
        "/api/v1/profiles",
        json={
            "phone": "8 999-888-77-66",
            "first_name": "Valerii",
            "last_name": "Semenov",
        },
    )

    assert response.status_code == 201

    profile_service_mock.create_profile.assert_awaited_once()

    call = profile_service_mock.create_profile.await_args

    assert call is not None
    assert call.kwargs["user_id"] == user_id


@pytest.mark.asyncio
async def test_create_profile_with_invalid_jwt(
    client_with_invalid_jwt: AsyncClient,
    profile_service_mock: AsyncMock,
    user_id: uuid.UUID,
) -> None:
    response = await client_with_invalid_jwt.post(
        "/api/v1/profiles",
        json={
            "phone": "8 999-888-77-66",
            "first_name": "Valerii",
            "last_name": "Semenov",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired token",
    }
    profile_service_mock.create_profile.assert_not_awaited()

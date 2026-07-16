import datetime
import uuid
from unittest.mock import AsyncMock

import pytest
from profile_service.core.exceptions import (
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
)
from profile_service.entities.profiles import Profile
from profile_service.schemas.profiles import ProfileCreate, ProfileUpdate
from profile_service.services.profiles import ProfileService


@pytest.mark.asyncio
async def test_create_profile() -> None:
    repo = AsyncMock()
    repo.get_by_user_id.return_value = None
    repo.get_by_phone.return_value = None
    repo.create_profile.side_effect = lambda profile: profile

    service = ProfileService(repo=repo)

    user_id = uuid.uuid4()

    result = await service.create_profile(
        user_id=user_id,
        data=ProfileCreate(
            phone="8 999 777 66 55",
            first_name="John",
            middle_name=None,
            last_name="Doe",
        ),
    )

    assert isinstance(result, Profile)
    assert result.user_id == user_id
    assert result.phone == "+79997776655"

    repo.get_by_user_id.assert_awaited_once_with(user_id=user_id)
    repo.get_by_phone.assert_awaited_once_with(phone="+79997776655")
    repo.create_profile.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_profile_when_profile_exists() -> None:
    repo = AsyncMock()
    repo.get_by_user_id.return_value = object()
    user_id = uuid.uuid4()

    service = ProfileService(repo=repo)

    with pytest.raises(ProfileAlreadyExistsError):
        await service.create_profile(
            user_id=user_id,
            data=ProfileCreate(
                phone="8 999 777 66 55",
                first_name="John",
                middle_name=None,
                last_name="Doe",
            ),
        )

    repo.get_by_user_id.assert_awaited_once_with(user_id=user_id)
    repo.get_by_phone.assert_not_awaited()
    repo.create_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_profile_when_phone_exists() -> None:
    repo = AsyncMock()
    repo.get_by_user_id.return_value = None
    repo.get_by_phone.return_value = object()

    service = ProfileService(repo=repo)

    with pytest.raises(PhoneAlreadyExistsError):
        await service.create_profile(
            user_id=uuid.uuid4(),
            data=ProfileCreate(
                phone="8 999 777 66 55",
                first_name="John",
                middle_name=None,
                last_name="Doe",
            ),
        )

    repo.get_by_phone.assert_awaited_once_with(
        phone="+79997776655",
    )
    repo.create_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_profile() -> None:
    repo = AsyncMock()
    user_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.UTC)

    expected_profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79997776655",
        first_name="John",
        middle_name="Test",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    repo.get_by_user_id.return_value = expected_profile
    service = ProfileService(repo=repo)

    result = await service.get_by_user_id(user_id=user_id)

    assert result == expected_profile
    repo.get_by_user_id.assert_awaited_once_with(user_id=user_id)


@pytest.mark.asyncio
async def test_get_not_found_profile() -> None:
    repo = AsyncMock()
    repo.get_by_user_id.return_value = None
    user_id = uuid.uuid4()
    service = ProfileService(repo=repo)

    with pytest.raises(ProfileNotFoundError):
        await service.get_by_user_id(user_id=user_id)

    repo.get_by_user_id.assert_awaited_once_with(user_id=user_id)


@pytest.mark.asyncio
async def test_update_profile() -> None:
    repo = AsyncMock()
    user_id = uuid.uuid4()

    now = datetime.datetime.now(datetime.UTC)

    existing_profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79997776655",
        first_name="John",
        middle_name="Test",
        last_name="DoeDoe",
        created_at=now,
        updated_at=now,
    )
    repo.get_by_user_id.return_value = existing_profile
    repo.get_by_phone.return_value = None
    repo.update_profile.side_effect = lambda profile: profile

    service = ProfileService(repo=repo)

    data = ProfileUpdate(
        phone="8 999 777 66 55",
        first_name="Johnny",
        middle_name=None,
        last_name="Doe",
    )

    result = await service.update_profile(user_id=user_id, data=data)

    assert isinstance(result, Profile)
    assert result.id == existing_profile.id
    assert result.user_id == user_id
    assert result.phone == "+79997776655"
    assert result.first_name == "Johnny"
    assert result.middle_name is None
    assert result.last_name == "Doe"
    assert result.created_at == existing_profile.created_at
    assert result.updated_at >= existing_profile.updated_at
    repo.get_by_user_id.assert_awaited_once_with(user_id=user_id)
    repo.get_by_phone.assert_not_awaited()
    repo.update_profile.assert_awaited_once_with(profile=result)


@pytest.mark.asyncio
async def test_update_profile_with_new_phone() -> None:
    repo = AsyncMock()
    user_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.UTC)

    existing_profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79997776655",
        first_name="John",
        middle_name="Test",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    repo.get_by_user_id.return_value = existing_profile
    repo.get_by_phone.return_value = None
    repo.update_profile.side_effect = lambda profile: profile

    service = ProfileService(repo=repo)

    result = await service.update_profile(
        user_id=user_id,
        data=ProfileUpdate(
            phone="8 999 111-22-33",
            first_name="John",
            middle_name="Test",
            last_name="Doe",
        ),
    )

    assert result.phone == "+79991112233"
    assert result.first_name == existing_profile.first_name
    assert result.middle_name == existing_profile.middle_name
    assert result.last_name == existing_profile.last_name

    repo.get_by_phone.assert_awaited_once_with(
        phone="+79991112233",
    )
    repo.update_profile.assert_awaited_once_with(profile=result)


@pytest.mark.asyncio
async def test_update_profile_when_profile_not_found() -> None:
    repo = AsyncMock()
    repo.get_by_user_id.return_value = None

    service = ProfileService(repo=repo)
    user_id = uuid.uuid4()

    with pytest.raises(ProfileNotFoundError):
        await service.update_profile(
            user_id=user_id,
            data=ProfileUpdate(phone="8 999 111-22-33"),
        )

    repo.get_by_user_id.assert_awaited_once_with(user_id=user_id)
    repo.get_by_phone.assert_not_awaited()
    repo.update_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_profile_when_new_phone_exists() -> None:
    repo = AsyncMock()
    user_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.UTC)

    existing_profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79997776655",
        first_name="John",
        middle_name=None,
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    repo.get_by_user_id.return_value = existing_profile
    repo.get_by_phone.return_value = object()

    service = ProfileService(repo=repo)

    with pytest.raises(PhoneAlreadyExistsError):
        await service.update_profile(
            user_id=user_id,
            data=ProfileUpdate(phone="8 999 111-22-33"),
        )

    repo.get_by_phone.assert_awaited_once_with(
        phone="+79991112233",
    )
    repo.update_profile.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_only_first_name() -> None:
    repo = AsyncMock()
    user_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.UTC)

    existing_profile = Profile(
        id=uuid.uuid4(),
        user_id=user_id,
        phone="+79997776655",
        first_name="John",
        middle_name="Test",
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )

    repo.get_by_user_id.return_value = existing_profile
    repo.update_profile.side_effect = lambda profile: profile

    service = ProfileService(repo=repo)

    result = await service.update_profile(
        user_id=user_id,
        data=ProfileUpdate(first_name="Johnny"),
    )

    assert result.first_name == "Johnny"
    assert result.phone == existing_profile.phone
    assert result.middle_name == existing_profile.middle_name
    assert result.last_name == existing_profile.last_name

    repo.update_profile.assert_awaited_once_with(profile=result)
    repo.get_by_phone.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_profile() -> None:
    repo = AsyncMock()
    service = ProfileService(repo=repo)
    user_id = uuid.uuid4()

    await service.delete_profile(user_id=user_id)

    repo.delete_profile.assert_awaited_once_with(user_id=user_id)

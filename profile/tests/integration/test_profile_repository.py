import dataclasses
import datetime
import uuid

import pytest
from profile_service.core.exceptions import (
    PhoneAlreadyExistsError,
    ProfileAlreadyExistsError,
)
from profile_service.entities.profiles import Profile
from profile_service.repositories.profiles import ProfileRepo
from sqlalchemy.ext.asyncio import AsyncSession


def make_profile(
    *,
    user_id: uuid.UUID | None = None,
    phone: str = "+79991112233",
) -> Profile:
    now = datetime.datetime.now(datetime.UTC)

    return Profile(
        id=uuid.uuid4(),
        user_id=user_id or uuid.uuid4(),
        phone=phone,
        first_name="John",
        middle_name=None,
        last_name="Doe",
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_profile(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    profile = make_profile()

    result = await repo.create_profile(profile)

    assert result == profile


@pytest.mark.asyncio
async def test_create_profile_persists_data(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    profile = make_profile()
    await repo.create_profile(profile)
    saved_profile = await repo.get_by_user_id(profile.user_id)
    assert saved_profile == profile


@pytest.mark.asyncio
async def test_get_profile_by_user_id(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    profile = make_profile()
    await repo.create_profile(profile)
    result = await repo.get_by_user_id(profile.user_id)
    assert result == profile


@pytest.mark.asyncio
async def test_get_profile_by_user_id_returns_none(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    result = await repo.get_by_user_id(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_profile_by_phone(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    profile = make_profile(phone="+79995554433")
    await repo.create_profile(profile)
    result = await repo.get_by_phone("+79995554433")
    assert result == profile


@pytest.mark.asyncio
async def test_create_profile_with_duplicate_user_id(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    user_id = uuid.uuid4()
    first_profile = make_profile(
        user_id=user_id,
        phone="+79991112233",
    )
    second_profile = make_profile(
        user_id=user_id,
        phone="+79992223344",
    )
    await repo.create_profile(first_profile)
    with pytest.raises(ProfileAlreadyExistsError):
        await repo.create_profile(second_profile)


@pytest.mark.asyncio
async def test_create_profile_with_duplicate_phone(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    phone = "+79991112233"

    first_profile = make_profile(phone=phone)
    second_profile = make_profile(phone=phone)

    await repo.create_profile(first_profile)

    with pytest.raises(PhoneAlreadyExistsError):
        await repo.create_profile(second_profile)


@pytest.mark.asyncio
async def test_update_profile(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    profile = make_profile()

    await repo.create_profile(profile)

    updated_at = datetime.datetime.now(datetime.UTC)

    changed_profile = dataclasses.replace(
        profile,
        first_name="Frank",
        middle_name="Robert",
        phone="+79998887766",
        updated_at=updated_at,
    )

    result = await repo.update_profile(changed_profile)

    assert result.first_name == "Frank"
    assert result.middle_name == "Robert"
    assert result.phone == "+79998887766"
    assert result.updated_at == updated_at

    saved_profile = await repo.get_by_user_id(profile.user_id)

    assert saved_profile == result


@pytest.mark.asyncio
async def test_update_profile_with_duplicate_phone(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)

    first_profile = make_profile(phone="+79991112233")
    second_profile = make_profile(phone="+79992223344")

    await repo.create_profile(first_profile)
    await repo.create_profile(second_profile)

    changed_profile = dataclasses.replace(
        second_profile,
        phone=first_profile.phone,
        updated_at=datetime.datetime.now(datetime.UTC),
    )

    with pytest.raises(PhoneAlreadyExistsError):
        await repo.update_profile(changed_profile)


@pytest.mark.asyncio
async def test_delete_profile(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    profile = make_profile()
    await repo.create_profile(profile)
    await repo.delete_profile(profile.user_id)
    result = await repo.get_by_user_id(profile.user_id)
    assert result is None


@pytest.mark.asyncio
async def test_delete_missing_profile(
    integration_session: AsyncSession,
) -> None:
    repo = ProfileRepo(session=integration_session)
    await repo.delete_profile(uuid.uuid4())

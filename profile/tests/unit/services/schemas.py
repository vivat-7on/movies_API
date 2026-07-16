import pytest
from profile_service.schemas.profiles import ProfileUpdate
from pydantic import ValidationError


def test_profile_update_requires_at_least_one_field() -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProfileUpdate()

    assert "At least one field is required" in str(exc_info.value)


def test_profile_update_allows_single_field() -> None:
    data = ProfileUpdate(first_name="Frank")

    assert data.first_name == "Frank"
    assert data.model_fields_set == {"first_name"}


def test_profile_update_allows_null_middle_name() -> None:
    data = ProfileUpdate(middle_name=None)

    assert data.middle_name is None
    assert data.model_fields_set == {"middle_name"}
    assert data.model_dump(exclude_unset=True) == {"middle_name": None}


@pytest.mark.parametrize(
    "field_name",
    [
        "phone",
        "first_name",
        "last_name",
    ],
)
def test_profile_update_reject_null_required_fields(field_name: str) -> None:
    with pytest.raises(ValidationError) as exc_info:
        ProfileUpdate(**{field_name: None})

    assert f"Field {field_name} cannot be null" in str(exc_info.value)


def test_profile_update_excludes_missing_fields() -> None:
    data = ProfileUpdate(first_name="Frank")

    assert data.model_dump(exclude_unset=True) == {"first_name": "Frank"}

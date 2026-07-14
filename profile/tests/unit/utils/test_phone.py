import pytest
from profile_service.core.exceptions import InvalidPhoneNumberError
from profile_service.core.utils import normalize_phone


@pytest.mark.parametrize(
    ("raw_phone", "expected"),
    [
        ("8 999 111-22-33", "+79991112233"),
        ("+7 (999) 111-22-33", "+79991112233"),
        ("9991112233", "+79991112233"),
    ],
)
def test_normalize_phone(raw_phone: str, expected: str) -> None:
    assert normalize_phone(raw_phone) == expected


@pytest.mark.parametrize(
    "raw_phone",
    [
        "",
        "abc",
        "123",
        "+7 000 000-00-00",
    ],
)
def test_normalize_phone_invalid_number(raw_phone: str) -> None:
    with pytest.raises(InvalidPhoneNumberError):
        normalize_phone(raw_phone)


def test_normalize_phone_with_explicit_region() -> None:
    assert (
        normalize_phone(
            "202-555-0123",
            default_region="US",
        )
        == "+12025550123"
    )

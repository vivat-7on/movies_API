from profile.core.exceptions import InvalidPhoneNumberError

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


def normalize_phone(phone: str, default_region: str = "RU") -> str:
    """
    Normalize phone number to E.164 format.

    >>> normalize_phone('8 999 111-22-33')
    '+79991112233'

    >>> normalize_phone('+7 (999) 111-22-33')
    '+79991112233'

    """
    try:
        parsed_phone = phonenumbers.parse(phone, default_region)
    except NumberParseException as exc:
        raise InvalidPhoneNumberError("invalid phone number") from exc

    if not phonenumbers.is_valid_number(parsed_phone):
        raise InvalidPhoneNumberError("invalid phone number")

    return phonenumbers.format_number(parsed_phone, PhoneNumberFormat.E164)

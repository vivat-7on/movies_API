class DomainError(Exception):
    status_code = 400
    default_message = "Domain error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class ProfileAlreadyExistsError(DomainError):
    status_code = 409
    default_message = "Profile already exists"


class PhoneAlreadyExistsError(DomainError):
    status_code = 409
    default_message = "Phone already exists"


class InvalidPhoneNumberError(DomainError):
    status_code = 422
    default_message = "Invalid phone number"

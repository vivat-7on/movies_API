from ugc_content_api.exceptions.base import DomainError


class ReviewNotFound(DomainError):
    status_code = 404


class ReviewForbiddenError(DomainError):
    status_code = 403


class VoteNotFound(DomainError):
    status_code = 404

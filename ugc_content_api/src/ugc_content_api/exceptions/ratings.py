from ugc_content_api.exceptions.base import DomainError


class ScoreNotFound(DomainError):
    status_code = 404


class ScoreForbiddenError(DomainError):
    status_code = 403

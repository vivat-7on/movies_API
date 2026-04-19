import os
from logging import config as logging_config

from .logger import LOGGING


def setup_logging() -> None:
    logging_config.dictConfig(LOGGING)


PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

ELASTIC_HOST = os.getenv("ES_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ES_PORT", 9200))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt",
)
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

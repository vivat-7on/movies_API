from profile_service.db.connection import (
    create_async_engine_from_settings,
    create_session_factory,
)
from profile_service.db.settings import get_postgres_settings

postgres_settings = get_postgres_settings()
async_engine = create_async_engine_from_settings(settings=postgres_settings)
session_factory = create_session_factory(async_engine=async_engine)

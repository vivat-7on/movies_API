import psycopg2
from psycopg2.extensions import connection as PgConnection

from src.etl.db.settings import DBSettings


def create_pg_connection(settings: DBSettings) -> PgConnection:
    return psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        dbname=settings.POSTGRES_DB,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        connect_timeout=5,
    )

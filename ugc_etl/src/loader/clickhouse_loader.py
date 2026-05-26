import json
import logging
import re
import time
from datetime import datetime
from typing import Any, Callable, TypeVar

from clickhouse_driver import Client

logger = logging.getLogger(__name__)

T = TypeVar("T")
VALID_IDENTIFIER = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")


def retry_with_backoff(
    func: Callable[[], T],
    retries: int = 3,
    delay_seconds: float = 1.0,
) -> T:
    last_exception = None

    for attempt in range(1, retries + 1):
        try:
            return func()
        except Exception as exc:
            last_exception = exc
            logger.exception(
                "ClickHouse operation failed. Attempt %s/%s",
                attempt,
                retries,
            )
            time.sleep(delay_seconds * attempt)

    if last_exception is not None:
        raise last_exception

    raise RuntimeError("ClickHouse operation failed")


def create_clickhouse_client(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> Client:
    return Client(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


class ClickHouseLoader:
    def __init__(self, clickhouse_client: Client, table: str) -> None:
        if not VALID_IDENTIFIER.fullmatch(table):
            raise ValueError("Invalid ClickHouse table name")

        self.client = clickhouse_client
        self.table = table

    def create_events_table(self) -> None:
        self.client.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table} (
            event_type String,
            user_id Nullable(UUID),
            anonymous_id Nullable(String),
            timestamp DateTime,
            movie_id Nullable(String),
            page_url Nullable(String),
            duration_seconds Nullable(Int32),
            video_quality Nullable(String),
            filter_name Nullable(String),
            filter_value Nullable(String),
            payload String
            )
            ENGINE = MergeTree
            PARTITION BY toYYYYMM(timestamp)
            ORDER BY (timestamp, event_type);
            """,
        )

    def insert_batch(self, data: list[dict[str, Any]]) -> None:
        if not data:
            return

        rows = [
            (
                row["event_type"],
                row.get("user_id"),
                row.get("anonymous_id"),
                datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")),
                row["payload"].get("movie_id"),
                row["payload"].get("page_url"),
                row["payload"].get("duration_seconds"),
                row["payload"].get("video_quality"),
                row["payload"].get("filter_name"),
                row["payload"].get("filter_value"),
                json.dumps(row["payload"]),
            )
            for row in data
        ]

        retry_with_backoff(
            lambda: self.client.execute(
                f"INSERT INTO {self.table} VALUES",
                rows,
            ),
            retries=3,
            delay_seconds=1.0,
        )

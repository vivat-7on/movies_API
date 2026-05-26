import json
from datetime import datetime
from typing import Any

from clickhouse_driver import Client


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
                json.dumps(row["payload"]),
            )
            for row in data
        ]
        self.client.execute(
            f"INSERT INTO {self.table} VALUES",
            rows,
        )

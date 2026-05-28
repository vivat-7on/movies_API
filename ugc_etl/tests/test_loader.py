import pytest
from loader.clickhouse_loader import ClickHouseLoader


class FakeClickHouseClient:
    def __init__(self):
        self.queries = []

    def execute(self, query, data=None):
        self.queries.append((query, data))


def test_insert_batch_insert_rows():
    client = FakeClickHouseClient()
    loader = ClickHouseLoader(client, table="events")

    loader.insert_batch(
        [
            {
                "event_type": "page_view",
                "user_id": None,
                "anonymous_id": "anon-1",
                "timestamp": "2026-05-22T12:00:00Z",
                "payload": {
                    "page_url": "/movies/123",
                    "duration_seconds": 42,
                },
            },
        ],
    )

    query, rows = client.queries[0]
    assert "INSERT INTO events VALUES" in query
    assert len(rows) == 1
    assert rows[0][0] == "page_view"
    assert rows[0][1] is None
    assert rows[0][2] == "anon-1"
    assert rows[0][5] == "/movies/123"
    assert rows[0][6] == 42


def test_insert_batch_does_nothing_for_empty_batch():
    client = FakeClickHouseClient()
    loader = ClickHouseLoader(client, table="events")

    loader.insert_batch([])

    assert client.queries == []


def test_create_events_table():
    client = FakeClickHouseClient()
    loader = ClickHouseLoader(client, table="events")

    loader.create_events_table()

    query, rows = client.queries[0]

    assert "CREATE TABLE IF NOT EXISTS events" in query
    assert rows is None


def test_loader_rejects_invalid_table_name():
    client = FakeClickHouseClient()

    with pytest.raises(ValueError):
        ClickHouseLoader(client, table="events; DROP TABLE events")

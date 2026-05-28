import pytest
from main import flush_batch


class FakeKafkaConsumer:
    def __init__(self):
        self.commit_called = 0

    def commit(self):
        self.commit_called += 1


class FakeLoader:
    def __init__(self):
        self.inserted = []

    def insert_batch(self, data):
        self.inserted.append(list(data))


class FailingLoader:
    def insert_batch(self, data):
        raise RuntimeError("ClickHouse unavailable")


def test_flush_batch_inserts_data_commits_offset_and_clears_batch():
    batch = [{"event_type": "page_view"}]
    loader = FakeLoader()
    consumer = FakeKafkaConsumer()

    flush_batch(batch, loader, consumer)

    assert consumer.commit_called == 1
    assert loader.inserted == [[{"event_type": "page_view"}]]
    assert batch == []


def test_flush_batch_does_nothing_for_empty_batch():
    batch = []
    loader = FakeLoader()
    consumer = FakeKafkaConsumer()

    flush_batch(batch, loader, consumer)

    assert loader.inserted == []
    assert consumer.commit_called == 0


def test_flush_batch_does_not_commit_offset_if_insert_failed():
    batch = [{"event_type": "page_view"}]
    loader = FailingLoader()
    consumer = FakeKafkaConsumer()

    with pytest.raises(RuntimeError):
        flush_batch(batch, loader, consumer)

    assert consumer.commit_called == 0
    assert batch == [{"event_type": "page_view"}]

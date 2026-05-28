from app.app import create_app


class FakeFuture:
    def get(self, timeout=None):
        return None


class FakeProducer:
    def __init__(self):
        self.sent = []

    def send(self, data):
        self.sent.append(data)
        return FakeFuture()

    def is_ready(self):
        return True


class FakeAuth:
    def __init__(self, user_id=None):
        self.user_id = user_id

    def get_user_id_from_token(self, auth_header):
        return self.user_id


class FailingFuture:
    def get(self, timeout=None):
        raise RuntimeError("Kafka unavailable")


class FailingProducer:
    def send(self, data):
        return FailingFuture()

    def is_ready(self):
        return False


def test_anonymous_event_is_sent_to_kafka():
    producer = FakeProducer()
    auth = FakeAuth()

    app = create_app(producer, auth)
    client = app.test_client()

    _id = "f668e966-f64a-422f-abf8-5e39d4aa662a"

    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "page_view",
            "anonymous_id": _id,
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert response.status_code == 201
    assert len(producer.sent) == 1
    assert producer.sent[0]["event_type"] == "page_view"
    assert producer.sent[0]["anonymous_id"] == _id
    assert producer.sent[0]["user_id"] is None


def test_event_is_sent_to_kafka():
    user_id = "f668e966-f64a-422f-abf8-5e39d4aa662a"
    producer = FakeProducer()
    auth = FakeAuth(user_id=user_id)

    app = create_app(producer, auth)
    client = app.test_client()

    response = client.post(
        "/api/v1/events",
        headers={"Authorization": "Bearer <access_token>"},
        json={
            "event_type": "page_view",
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert response.status_code == 201
    assert len(producer.sent) == 1
    assert producer.sent[0]["event_type"] == "page_view"
    assert producer.sent[0]["user_id"] == user_id


def test_request_without_token_and_anonymous_id():
    producer = FakeProducer()
    auth = FakeAuth()

    app = create_app(producer, auth)
    client = app.test_client()

    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "page_view",
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert response.status_code == 422


def test_invalid_event_type():
    producer = FakeProducer()
    auth = FakeAuth()

    app = create_app(producer, auth)
    client = app.test_client()

    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "invalid_event",
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert response.status_code == 422


def test_kafka_unavailable_returns_503():
    producer = FailingProducer()
    auth = FakeAuth()

    app = create_app(producer, auth)
    client = app.test_client()

    response = client.post(
        "/api/v1/events",
        json={
            "event_type": "page_view",
            "anonymous_id": "anon-1",
            "timestamp": "2026-05-22T12:00:00Z",
            "payload": {"page_url": "/movies/123"},
        },
    )

    assert response.status_code == 503
    assert response.get_json() == {"error": "Kafka is unavailable"}


def test_ready_returns_503_when_producer_not_ready():
    producer = FailingProducer()
    auth = FakeAuth()

    app = create_app(producer, auth)
    client = app.test_client()

    response = client.get("/ready")

    assert response.status_code == 503


def test_health_returns_200():
    app = create_app(FakeProducer(), FakeAuth())
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}

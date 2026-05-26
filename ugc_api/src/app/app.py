from auth.auth import Auth
from auth.settings import AuthSettings
from flask import Flask, jsonify, request
from jose import JWTError
from producer.producer import KafkaEventProducer, create_kafka_producer
from producer.settings import KafkaSettings
from pydantic import ValidationError

from app.schemas import EventIn, EventMessage

app = Flask(__name__)

kafka_settings = KafkaSettings()
auth_settings = AuthSettings()

raw_producer = create_kafka_producer(
    bootstrap_servers=kafka_settings.kafka_bootstrap_servers,
)

event_producer = KafkaEventProducer(
    producer=raw_producer,
    topic=kafka_settings.KAFKA_TOPIC,
)
auth = Auth(settings=auth_settings)


@app.post("/api/v1/events")
def events():
    auth_header = request.headers.get("Authorization")

    try:
        user_id = auth.get_user_id_from_token(auth_header)
    except (JWTError, ValueError):
        return jsonify({"error": "Invalid token"}), 401

    try:
        event = EventIn.model_validate(request.get_json())
    except ValidationError as exc:
        return jsonify({"error": exc.errors()}), 422

    if user_id is None and event.anonymous_id is None:
        return jsonify({"error": "anonymous_id is required"}), 422

    event_message = EventMessage(
        **event.model_dump(),
        user_id=user_id,
    )

    try:
        event_producer.send(data=event_message.model_dump(mode="json"))
    except Exception:
        app.logger.exception("Failed to send event to Kafka")
        return jsonify({"error": "Kafka is unavailable"}), 503

    return jsonify({"message": "sent"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0")

from flask import Flask, jsonify, request
from producer.producer import KafkaEventProducer, create_kafka_producer
from producer.settings import KafkaSettings
from pydantic import ValidationError

from app.schemas import Event

app = Flask(__name__)

kafka_settings = KafkaSettings()
raw_producer = create_kafka_producer(
    bootstrap_servers=kafka_settings.kafka_bootstrap_servers,
)

event_producer = KafkaEventProducer(
    producer=raw_producer,
    topic=kafka_settings.KAFKA_TOPIC,
)


@app.post("/api/v1/events")
def events():
    try:
        event = Event.model_validate(request.get_json())
    except ValidationError as exc:
        return jsonify({"error": exc.errors()}), 422

    try:
        event_producer.send(data=event.model_dump(mode="json"))
    except Exception:
        return jsonify({"error": "Kafka is unavailable"}), 503
    return jsonify({"message": "sent"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0")

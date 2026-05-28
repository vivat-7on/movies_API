import atexit

from auth.auth import Auth
from auth.settings import AuthSettings
from flask import Flask
from producer.producer import KafkaEventProducer, create_kafka_producer
from producer.settings import KafkaSettings

from app.routes import events_bp


def create_real_event_producer() -> KafkaEventProducer:
    kafka_settings = KafkaSettings()
    raw_producer = create_kafka_producer(
        bootstrap_servers=kafka_settings.kafka_bootstrap_servers
    )

    event_producer = KafkaEventProducer(
        producer=raw_producer,
        topic=kafka_settings.KAFKA_TOPIC,
    )

    atexit.register(event_producer.close)

    return event_producer


def create_app(event_producer=None, auth=None) -> Flask:
    app = Flask(__name__)

    app.config["event_producer"] = event_producer or create_real_event_producer()
    app.config["auth"] = auth or Auth(settings=AuthSettings())

    app.register_blueprint(events_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0")

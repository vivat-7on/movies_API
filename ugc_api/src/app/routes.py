from flask import Blueprint, current_app, jsonify, request
from jose import JWTError
from pydantic import ValidationError

from app.schemas import EventIn, EventMessage

events_bp = Blueprint("events", __name__)


@events_bp.post("/api/v1/events")
def events():
    auth = current_app.config["auth"]
    event_producer = current_app.config["event_producer"]

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
        future = event_producer.send(data=event_message.model_dump(mode="json"))
        future.get(timeout=1)
    except Exception:
        current_app.logger.exception("Failed to send event to Kafka")
        return jsonify({"error": "Kafka is unavailable"}), 503

    return jsonify({"message": "sent"}), 201


@events_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@events_bp.get("/ready")
def ready():
    event_producer = current_app.config.get("event_producer")
    if event_producer.is_ready():
        return jsonify({"status": "ready"}), 200

    return jsonify({"status": "not_ready"}), 503

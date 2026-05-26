import logging
import time

from consumer.kafka_consumer import create_kafka_consumer
from loader.clickhouse_loader import ClickHouseLoader, create_clickhouse_client
from pydantic import ValidationError
from schemas import EventMessage
from settings import Settings

logger = logging.getLogger(__name__)


def flush_batch(batch, loader, consumer) -> None:
    if not batch:
        return

    loader.insert_batch(batch)
    consumer.commit()
    logger.info("Insert batch", extra={"batch_size": len(batch)})
    batch.clear()


def main():
    config = Settings()
    consumer = create_kafka_consumer(
        topics=config.KAFKA_TOPIC,
        bootstrap_servers=config.kafka_bootstrap_servers,
        auto_offset_reset="earliest",
        group_id=config.KAFKA_GROUP_ID,
    )

    clickhouse_client = create_clickhouse_client(
        host=config.CLICKHOUSE_HOST,
        port=config.CLICKHOUSE_PORT,
        user=config.CLICKHOUSE_USER,
        password=config.CLICKHOUSE_PASSWORD,
        database=config.CLICKHOUSE_DB,
    )

    loader = ClickHouseLoader(
        clickhouse_client=clickhouse_client,
        table=config.CLICKHOUSE_TABLE,
    )

    loader.create_events_table()
    batch = []
    last_flush_at = time.monotonic()

    try:
        for message in consumer:
            try:
                event = EventMessage.model_validate(message.value)
            except ValidationError as exc:
                logger.exception(
                    "Invalid event skipped",
                    exc,
                    extra={
                        "topic": message.topic,
                        "partition": message.partition,
                        "offset": message.offset,
                    },
                )
                consumer.commit()
                continue

            batch.append(event.model_dump(mode="json"))

            now = time.monotonic()
            should_flush_by_size = len(batch) >= config.BATCH_SIZE
            should_flush_by_time = now - last_flush_at >= config.BATCH_TIMEOUT_SECONDS

            if should_flush_by_size or should_flush_by_time:
                flush_batch(batch, loader, consumer)
                last_flush_at = time.monotonic()
    except KeyboardInterrupt:
        logger.info("ETL stopped by user")
    except Exception:
        logger.exception("ETL failed")
        raise
    finally:
        flush_batch(batch, loader, consumer)
        consumer.close()


if __name__ == "__main__":
    main()

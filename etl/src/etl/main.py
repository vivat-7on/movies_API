import logging
import os
import time
import uuid

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

from etl.es.loader import ElasticsearchLoader
from etl.db.settings import DBSettings
from etl.state.state import State
from etl.db.connection import create_pg_connection
from etl.db.extractor import PostgresExtractor
from etl.es.settings import EsSettings
from etl.dto.dto import FilmWorkDTO
from etl.state.storage import JsonFileStorage
from etl.transformer.film_work import transform_film_work

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "DEBUG"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", 10))


def run_once(
    state: State,
    loader: ElasticsearchLoader,
    db_settings: DBSettings,
):
    conn = create_pg_connection(settings=db_settings)
    psycopg2.extras.register_uuid(conn_or_curs=conn)
    try:
        # получаем состояние из хранилища
        film_work_ts = state.get("film_work_ts")
        genre_ts = state.get("genre_ts")
        person_ts = state.get("person_ts")
        genre_film_work_ts = state.get("genre_film_work_ts")
        person_film_work_ts = state.get("person_film_work_ts")

        # получаем данные
        extractor = PostgresExtractor(connection=conn)
        all_film_work_ids: set[uuid.UUID] = set()

        ids, film_work_ts = extractor.fetch_changed_film_work_ids(
            film_work_ts=film_work_ts,
        )
        all_film_work_ids |= ids

        ids, genre_ts = extractor.fetch_film_work_ids_by_changed_genres(
            genre_ts=genre_ts,
        )
        all_film_work_ids |= ids

        ids, person_ts = extractor.fetch_film_work_ids_by_changed_persons(
            person_ts=person_ts,
        )
        all_film_work_ids |= ids

        ids, genre_film_work_ts = extractor.fetch_film_work_ids_by_changed_genre_film_work(
            genre_film_work_ts=genre_film_work_ts,
        )
        all_film_work_ids |= ids

        ids, person_film_work_ts = extractor.fetch_film_work_ids_by_changed_person_film_work(
            person_film_work_ts=person_film_work_ts,
        )
        all_film_work_ids |= ids

        if not all_film_work_ids:
            logger.info("No changes detected")
            return

        changed_film_works: list[FilmWorkDTO] = extractor.fetch_film_work_for_index(
            film_work_ids=all_film_work_ids,
        )

        # трансформируем данные
        film_work_documents: list[dict] = []
        for film_work in changed_film_works:
            transformed_film_work = transform_film_work(film_work=film_work)
            film_work_documents.append(
                transformed_film_work.model_dump(mode="json")
            )

        # загружаем данные
        loader.ensure_index()
        loader.bulk_load(film_work_documents)

        # сохраняем состояние
        state.set("film_work_ts", film_work_ts)
        state.set("genre_ts", genre_ts)
        state.set("person_ts", person_ts)
        state.set("genre_film_work_ts", genre_film_work_ts)
        state.set("person_film_work_ts", person_film_work_ts)

    finally:
        conn.close()

def main():
    db_settings = DBSettings()
    es_settings = EsSettings()

    storage_file_name = os.getenv("STORAGE_FILE_NAME", "state.json")
    storage = JsonFileStorage(file_name=storage_file_name)

    state = State(storage=storage)

    es_host = es_settings.ES_HOST
    es_port = es_settings.ES_PORT
    index_name = es_settings.ES_INDEX
    client = Elasticsearch(f"http://{es_host}:{es_port}")
    loader = ElasticsearchLoader(client=client, index_name=index_name)

    logger.info("ETL service started")
    while True:
        try:
            run_once(state=state, loader=loader, db_settings=db_settings)
            time.sleep(POLL_INTERVAL_SECONDS)
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            logger.warning("Postgres unavailable, backing off")
            time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()

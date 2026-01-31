import datetime
import logging
import uuid

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import RealDictCursor

from etl.dto.dto import FilmWorkDTO, PersonDTO, GenreDTO, FilmPersonDTO

logger = logging.getLogger(__name__)


class PostgresExtractor:
    def __init__(self, connection: PgConnection) -> None:
        self.conn = connection

    def fetch_changed_film_work_ids(
        self,
        film_work_ts: datetime.datetime | None = None,
        ) -> tuple[set[uuid.UUID], datetime.datetime | None]:
        sql = """
              SELECT fw.id, fw.updated_at
              FROM content.film_work fw
              WHERE (%s IS NULL OR updated_at > %s)
              ORDER BY fw.updated_at ASC;
              """
        film_work_ids: set[uuid.UUID] = set()
        max_film_work_ts: datetime.datetime | None = film_work_ts
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (film_work_ts, film_work_ts))
                rows = cur.fetchall()

            for row in rows:
                film_work_ids.add(row["id"])
                updated_at = row["updated_at"]
                if max_film_work_ts is None or updated_at > max_film_work_ts:
                    max_film_work_ts = updated_at

            logger.info(
                "Fetched %d film_work ids after update film work, "
                "last updated_at=%s",
                len(film_work_ids),
                max_film_work_ts,
                )
            return film_work_ids, max_film_work_ts
        except Exception:
            logger.exception("Failed to fetch changed film_work_id")
            raise

    def fetch_film_work_ids_by_changed_genres(
        self,
        genre_ts: datetime.datetime | None = None,
        ) -> tuple[set[uuid.UUID], datetime.datetime | None]:
        sql = """
              SELECT gfw.film_work_id, g.updated_at
              FROM content.genre g
                       JOIN content.genre_film_work gfw ON g.id = gfw.genre_id
              WHERE (%s IS NULL OR g.updated_at > %s)
              ORDER BY g.updated_at ASC;
              """
        film_work_ids: set[uuid.UUID] = set()
        max_genre_ts: datetime.datetime | None = genre_ts

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (genre_ts, genre_ts))
                rows = cur.fetchall()

                for row in rows:
                    film_work_ids.add(row["film_work_id"])
                    updated_at = row["updated_at"]
                    if max_genre_ts is None or updated_at > max_genre_ts:
                        max_genre_ts = updated_at

                logger.info(
                    "Fetched %d film_work ids due to genre updates, "
                    "last updated_at=%s",
                    len(film_work_ids),
                    max_genre_ts,
                    )
                return film_work_ids, max_genre_ts
        except Exception:
            logger.exception("Failed to fetch changed genre")
            raise

    def fetch_film_work_ids_by_changed_persons(
        self,
        person_ts: datetime.datetime | None = None,
        ) -> tuple[set[uuid.UUID], datetime.datetime | None]:
        sql = """
              SELECT pfw.film_work_id, p.updated_at
              FROM content.person p
                       JOIN content.person_film_work pfw ON p.id = pfw.person_id
              WHERE (%s IS NULL OR p.updated_at > %s)
              ORDER BY p.updated_at ASC;
              """

        film_work_ids: set[uuid.UUID] = set()
        max_person_ts: datetime.datetime | None = person_ts

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (person_ts, person_ts))
                rows = cur.fetchall()

                for row in rows:
                    film_work_ids.add(row["film_work_id"])
                    updated_at = row["updated_at"]
                    if max_person_ts is None or updated_at > max_person_ts:
                        max_person_ts = updated_at

                logger.info(
                    "Fetched %d film_work ids due to person updates, "
                    "last updated_at=%s",
                    len(film_work_ids),
                    max_person_ts,
                    )
                return film_work_ids, max_person_ts
        except Exception:
            logger.exception("Failed to fetch changed person")
            raise

    def fetch_film_work_ids_by_changed_genre_film_work(
        self,
        genre_film_work_ts: datetime.datetime | None = None,
        ) -> tuple[set[uuid.UUID], datetime.datetime | None]:
        sql = """
              SELECT gfw.film_work_id, gfw.updated_at
              FROM content.genre_film_work gfw
              WHERE (%s IS NULL OR gfw.updated_at > %s)
              ORDER BY gfw.updated_at ASC;
              """
        film_work_ids: set[uuid.UUID] = set()
        max_genre_film_work_ts: datetime.datetime | None = genre_film_work_ts
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (genre_film_work_ts, genre_film_work_ts))
                rows = cur.fetchall()

                for row in rows:
                    film_work_ids.add(row["film_work_id"])
                    updated_at = row["updated_at"]
                    if max_genre_film_work_ts is None or updated_at > max_genre_film_work_ts:
                        max_genre_film_work_ts = updated_at

                logger.info(
                    "Fetched %d film_work ids due to genre film work updates, "
                    "last updated_at=%s",
                    len(film_work_ids),
                    max_genre_film_work_ts,
                    )
                return film_work_ids, max_genre_film_work_ts
        except Exception:
            logger.exception("Failed to fetch changed genre film work")
            raise

    def fetch_film_work_ids_by_changed_person_film_work(
        self,
        person_film_work_ts: datetime.datetime | None = None,
        ) -> tuple[set[uuid.UUID], datetime.datetime | None]:
        sql = """
              SELECT pfw.film_work_id, pfw.updated_at
              FROM content.person_film_work pfw
              WHERE (%s IS NULL OR pfw.updated_at > %s)
              ORDER BY pfw.updated_at ASC;
              """

        film_work_ids: set[uuid.UUID] = set()
        max_person_film_work_ts: datetime.datetime | None = person_film_work_ts

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (person_film_work_ts, person_film_work_ts))
                rows = cur.fetchall()

                for row in rows:
                    film_work_ids.add(row["film_work_id"])
                    updated_at = row["updated_at"]
                    if max_person_film_work_ts is None or updated_at > max_person_film_work_ts:
                        max_person_film_work_ts = updated_at

                logger.info(
                    "Fetched %d film_work ids due to person film work updates, "
                    "last updated_at=%s",
                    len(film_work_ids),
                    max_person_film_work_ts,
                    )
                return film_work_ids, max_person_film_work_ts
        except Exception:
            logger.exception("Failed to fetch changed person film work")
            raise

    def fetch_film_work_for_index(
        self,
        film_work_ids: set[uuid.UUID],
        ) -> list[FilmWorkDTO]:
        if not film_work_ids:
            return []

        sql = """
              SELECT fw.id,
                     fw.title,
                     fw.rating,
                     fw.description,
                     fw.updated_at,
                     COALESCE(
                             jsonb_agg(
                                 DISTINCT jsonb_build_object(
                            'id', g.id,
                            'name', g.name
                        )
                    ) FILTER(WHERE g.name IS NOT NULL),
                             '[]' ::jsonb
                     ) AS genres,
                     COALESCE(
                             jsonb_agg(
                                 DISTINCT jsonb_build_object(
                            'id', p.id,
                            'full_name', p.full_name,
                            'role', pfw.role
                        )
                    ) FILTER(WHERE p.full_name IS NOT NULL),
                             '[]' ::jsonb
                     ) AS persons
              FROM content.film_work fw
                       LEFT JOIN content.person_film_work pfw
                                 ON pfw.film_work_id = fw.id
                       LEFT JOIN content.genre_film_work gfw
                                 ON gfw.film_work_id = fw.id
                       LEFT JOIN content.genre g ON g.id = gfw.genre_id
                       LEFT JOIN content.person p ON p.id = pfw.person_id
              WHERE fw.id = ANY (%s::uuid[])
              GROUP BY fw.id;
              """
        film_work_list: list[FilmWorkDTO] = []
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (list(film_work_ids),))
                rows = cur.fetchall()

                for row in rows:
                    film_work_list.append(
                        FilmWorkDTO(
                            id=row["id"],
                            title=row["title"],
                            rating=row["rating"],
                            description=row["description"],
                            persons=[
                                FilmPersonDTO(
                                    id=uuid.UUID(person["id"]),
                                    full_name=person["full_name"],
                                    role=person["role"],
                                    ) for person in row["persons"]
                                ],
                            genres=[
                                GenreDTO(
                                    id=uuid.UUID(genre["id"]),
                                    name=genre["name"],
                                    ) for genre in row["genres"]
                                ],
                            updated_at=row["updated_at"],
                            ),
                        )

                logger.info(
                    "Fetched %d film_work by ids.",
                    len(film_work_list),
                    )
                return film_work_list
        except Exception:
            logger.exception("Failed to fetch film work by ids")
            raise

    def fetch_changed_genres(
        self,
        genres_ts: datetime.datetime | None = None,
        ) -> tuple[list[GenreDTO], datetime.datetime | None]:
        sql = """
              SELECT g.id, g.name, g.updated_at
              FROM content.genre g
              WHERE (%s IS NULL OR g.updated_at > %s)
              ORDER BY g.updated_at ASC;
              """

        genres: list[GenreDTO] = []
        max_genre_ts: datetime.datetime | None = genres_ts

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (genres_ts, genres_ts))
                rows = cur.fetchall()

                for row in rows:
                    genres.append(
                        GenreDTO(
                            id=row["id"],
                            name=row["name"],
                            ),
                        )
                    updated_at = row["updated_at"]
                    if max_genre_ts is None or max_genre_ts < updated_at:
                        max_genre_ts = updated_at

                logger.info(
                    "Fetched %d genres, "
                    "last updated_at=%s",
                    len(genres),
                    max_genre_ts,
                    )
                return genres, max_genre_ts
        except Exception:
            logger.exception("Failed to fetch genres")
            raise

    def fetch_changed_persons(
        self,
        persons_ts: datetime.datetime | None = None,
        ) -> tuple[list[PersonDTO], datetime.datetime | None]:
        sql = """
              SELECT p.id, p.full_name, p.updated_at
              FROM content.person p
              WHERE (%s IS NULL OR p.updated_at > %s)
              ORDER BY p.updated_at ASC;
              """
        persons: list[PersonDTO] = []
        max_persons_ts: datetime.datetime | None = persons_ts
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, (persons_ts, persons_ts))
                rows = cur.fetchall()

                for row in rows:
                    persons.append(
                        PersonDTO(
                            id=row["id"],
                            full_name=row["full_name"],
                            ),
                        )
                    updated_at = row["updated_at"]
                    if max_persons_ts is None or max_persons_ts < updated_at:
                        max_persons_ts = updated_at

                logger.info(
                    "Fetched %d persons, "
                    "last updated_at=%s",
                    len(persons),
                    max_persons_ts,
                    )
                return persons, max_persons_ts
        except Exception:
            logger.exception("Failed to fetch persons")
            raise

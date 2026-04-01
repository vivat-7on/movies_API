from enum import StrEnum

from etl.dto.dto import FilmWorkDTO
from etl.es.model import FilmEsDocument, EsPerson, EsGenre


class Roles(StrEnum):
    ACTOR = "actor"
    DIRECTOR = "director"
    WRITER = "writer"


def transform_film_work(film_work: FilmWorkDTO) -> FilmEsDocument:
    directors = [
        person for person in film_work.persons
        if person.role == Roles.DIRECTOR
        ]
    actors = [
        person for person in film_work.persons
        if person.role == Roles.ACTOR
        ]
    writers = [
        person for person in film_work.persons
        if person.role == Roles.WRITER
        ]
    document = FilmEsDocument(
        id=film_work.id,
        imdb_rating=film_work.rating,
        genres=[EsGenre(id=g.id, name=g.name) for g in film_work.genres],
        title=film_work.title,
        description=film_work.description,

        directors_names=list({p.full_name for p in directors}),
        actors_names=list({p.full_name for p in actors}),
        writers_names=list({p.full_name for p in writers}),

        directors=[EsPerson(id=p.id, name=p.full_name) for p in directors],
        actors=[EsPerson(id=p.id, name=p.full_name) for p in actors],
        writers=[EsPerson(id=p.id, name=p.full_name) for p in writers],
        )
    return document

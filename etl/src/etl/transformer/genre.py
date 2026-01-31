from etl.dto.dto import GenreDTO
from etl.es.model import EsGenre


def transform_genre(genre: GenreDTO) -> EsGenre:
    return EsGenre(
        id=genre.id,
        name=genre.name,
        )

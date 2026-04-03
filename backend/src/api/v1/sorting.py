from enum import Enum


class FilmSortOptions(str, Enum):
    imdb_rating_asc = "imdb_rating"
    imdb_rating_desc = "-imdb_rating"
    title_asc = "title"
    title_desc = "-title"


class GenreSortOptions(str, Enum):
    name_asc = "name"
    name_desc = "-name"


class PersonSortOptions(str, Enum):
    name_asc = "name"
    name_desc = "-name"

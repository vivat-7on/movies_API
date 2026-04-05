MAPPING_MOVIES = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "imdb_rating": {"type": "float"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "genres": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                },
            },
            "directors": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                },
            },
            "actors": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                },
            },
            "writers": {
                "type": "nested",
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "keyword"},
                },
            },
            "actors_names": {"type": "keyword"},
            "writers_names": {"type": "keyword"},
            "directors_names": {"type": "keyword"},
        },
    },
}

MAPPING_GENRES = {
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword",
            },
            "name": {
                "type": "text",
                "fields": {
                    "raw": {
                        "type": "keyword",
                    },
                },
            },
        },
    },
}

MAPPING_PERSONS = {
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword",
            },
            "name": {
                "type": "text",
                "fields": {
                    "raw": {
                        "type": "keyword",
                    },
                },
            },
        },
    },
}

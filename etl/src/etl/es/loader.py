import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from etl.utils.backoff import backoff

logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    def __init__(
        self,
        client: Elasticsearch,
        movies_index_name: str,
        genres_index_name: str,
        persons_index_name: str,
        ) -> None:
        self.client = client
        self.movies_index_name = movies_index_name
        self.genres_index_name = genres_index_name
        self.persons_index_name = persons_index_name

    @backoff()
    def ensure_movies_index(self) -> None:
        if self.client.indices.exists(index=self.movies_index_name):
            logger.debug("Index %s exists", self.movies_index_name)
            return

        body = {
            "settings": {
                "refresh_interval": "1s",
                "analysis": {
                    "filter": {
                        "english_stop": {
                            "type": "stop",
                            "stopwords": "_english_"
                            },
                        "english_stemmer": {
                            "type": "stemmer",
                            "language": "english"
                            },
                        "english_possessive_stemmer": {
                            "type": "stemmer",
                            "language": "possessive_english"
                            },
                        "russian_stop": {
                            "type": "stop",
                            "stopwords": "_russian_"
                            },
                        "russian_stemmer": {
                            "type": "stemmer",
                            "language": "russian"
                            }
                        },
                    "analyzer": {
                        "ru_en": {
                            "tokenizer": "standard",
                            "filter": [
                                "lowercase",
                                "english_stop",
                                "english_stemmer",
                                "english_possessive_stemmer",
                                "russian_stop",
                                "russian_stemmer"
                                ]
                            }
                        }
                    }
                },
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                        },
                    "imdb_rating": {
                        "type": "float"
                        },
                    "genres": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                                },
                            "name": {
                                "type": "text",
                                }
                            }
                        },
                    "title": {
                        "type": "text",
                        "analyzer": "ru_en",
                        "fields": {
                            "raw": {
                                "type": "keyword"
                                }
                            }
                        },
                    "description": {
                        "type": "text",
                        "analyzer": "ru_en"
                        },
                    "directors_names": {
                        "type": "text",
                        "analyzer": "ru_en"
                        },
                    "actors_names": {
                        "type": "text",
                        "analyzer": "ru_en"
                        },
                    "writers_names": {
                        "type": "text",
                        "analyzer": "ru_en"
                        },
                    "directors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                                },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en"
                                }
                            }
                        },
                    "actors": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                                },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en"
                                }
                            }
                        },
                    "writers": {
                        "type": "nested",
                        "dynamic": "strict",
                        "properties": {
                            "id": {
                                "type": "keyword"
                                },
                            "name": {
                                "type": "text",
                                "analyzer": "ru_en"
                                }
                            }
                        }
                    }
                }
            }

        try:
            self.client.indices.create(index=self.movies_index_name, body=body)
            logger.info("Created index %s", self.movies_index_name)
        except Exception:
            logger.error("Failed to create movies index")
            raise

    @backoff()
    def ensure_genres_index(self) -> None:
        if self.client.indices.exists(index=self.genres_index_name):
            logger.debug("Index %s exists", self.genres_index_name)
            return

        body = {
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                        },
                    "name": {
                        "type": "text",
                        "fields": {
                            "raw": {
                                "type": "keyword"
                                }
                            }
                        }
                    }
                }
            }
        try:
            self.client.indices.create(index=self.genres_index_name, body=body)
            logger.info("Created index %s", self.genres_index_name)
        except Exception:
            logger.error("Failed to create genres index")
            raise

    @backoff()
    def ensure_persons_index(self) -> None:
        if self.client.indices.exists(index=self.persons_index_name):
            logger.debug("Index %s exists", self.persons_index_name)
            return

        body = {
            "mappings": {
                "dynamic": "strict",
                "properties": {
                    "id": {
                        "type": "keyword"
                        },
                    "name": {
                        "type": "text",
                        "fields": {
                            "raw": {
                                "type": "keyword"
                                }
                            }
                        }
                    }
                }
            }
        try:
            self.client.indices.create(index=self.persons_index_name, body=body)
            logger.info("Created index %s", self.persons_index_name)
        except Exception:
            logger.error("Failed to create persons index")
            raise

    @backoff()
    def bulk_load(
        self,
        documents: list[dict],
        index_name: str,
        ) -> None:
        if not documents:
            logger.debug("No documents to load")
            return

        actions = [
            {
                "_index": index_name,
                "_id": str(doc["id"]),
                "_source": doc
                } for doc in documents
            ]
        success, errors = bulk(self.client, actions, raise_on_error=False)
        logger.info("Bulk result: success=%s", success)
        if errors:
            logger.error("Bulk errors: %s", errors[:3])

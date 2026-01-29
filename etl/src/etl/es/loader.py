import logging

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from etl.utils.backoff import backoff

logger = logging.getLogger(__name__)


class ElasticsearchLoader:
    def __init__(
            self,
            client: Elasticsearch,
            index_name: str,
    ) -> None:
        self.client = client
        self.index_name = index_name

    @backoff()
    def ensure_index(self) -> None:
        if self.client.indices.exists(index=self.index_name):
            logger.debug("Index %s exists", self.index_name)
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
                        "type": "keyword"
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
            self.client.indices.create(index=self.index_name, body=body)
            logger.info("Created index %s", self.index_name)
        except Exception:
            logger.error("Failed to create index")
            raise

    @backoff()
    def bulk_load(self, documents: list[dict]) -> None:
        if not documents:
            logger.debug("No documents to load")
            return

        actions = [
            {
                "_index": self.index_name,
                "_id": str(doc["id"]),
                "_source": doc
            } for doc in documents
        ]
        success, errors = bulk(self.client, actions, raise_on_error=False)
        logger.info("Bulk result: success=%s", success)
        if errors:
            logger.error("Bulk errors: %s", errors[:3])

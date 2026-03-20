import os
import time

from elasticsearch import Elasticsearch

HOST = os.getenv("ES_HOST", "localhost")
PORT = os.getenv("ES_PORT", "9200")

if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f"http://{HOST}:{PORT}")

    for _ in range(30):
        if es_client.ping():
            break
        time.sleep(1)
    else:
        raise RuntimeError("Elasticsearch is not available")

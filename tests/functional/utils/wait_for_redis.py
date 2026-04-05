import os
import time

import redis

HOST = os.getenv("REDIS_HOST", "localhost")
PORT = os.getenv("REDIS_PORT", "6379")

if __name__ == "__main__":
    client = redis.Redis(host=HOST, port=int(PORT), db=0)
    for _ in range(100):
        try:
            client.get("ping")
            break
        except redis.exceptions.ConnectionError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Redis is not available")

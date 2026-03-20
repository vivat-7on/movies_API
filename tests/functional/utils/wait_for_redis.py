import time

import redis

if __name__ == '__main__':
    client = redis.Redis(host='localhost', port=6379, db=0)
    for i in range(100):
        try:
            client.get("ping")
            break
        except redis.exceptions.ConnectionError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Redis is not available")

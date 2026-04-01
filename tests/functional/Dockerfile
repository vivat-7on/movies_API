FROM python:3.11-slim

WORKDIR /app

COPY /.env .

COPY . .

RUN pip install -r tests/functional/requirements.txt

CMD ["sh", "-c", \
"python tests/functional/utils/wait_for_es.py && \
 python tests/functional/utils/wait_for_redis.py && \
 pytest tests/functional/src -vv"]
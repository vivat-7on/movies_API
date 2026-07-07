FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./src ./src
COPY alembic.ini .
COPY alembic ./alembic

ENV PYTHONPATH=/app/src
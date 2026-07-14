FROM python:3.11-slim

ENV PYTHONPATH=/app/src \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./src ./src
COPY alembic.ini .
COPY ./alembic ./alembic

RUN addgroup --system app  && \
    adduser --system --ingroup app app && \
    chown -R app:app /app

USER app

CMD ["uvicorn", "profile_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
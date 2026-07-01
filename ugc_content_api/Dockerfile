FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY ./src ./src

ENV PYTHONPATH=/app/src

CMD ["uvicorn", "ugc_content_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
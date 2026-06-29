FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip % \
    pip install -r requirements.txt \

COPY . .

RUN ["uvicorn", "ugc_content_api.main:app", "--reload"]
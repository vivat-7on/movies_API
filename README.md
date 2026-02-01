# Movies ETL & API

Проект представляет собой сервис для загрузки данных о фильмах, жанрах и персоналиях из PostgreSQL в Elasticsearch (ETL), а также HTTP API для получения этих данных через FastAPI с кэшированием в Redis.

## Архитектура

Проект состоит из двух независимых сервисов:

1. **ETL-сервис**
   - Читает данные из PostgreSQL
   - Отслеживает изменения с помощью `updated_at`
   - Загружает данные в Elasticsearch
   - Сохраняет состояние (state) между запусками

2. **API-сервис**
   - Предоставляет HTTP API для фильмов, жанров и персоналий
   - Читает данные из Elasticsearch
   - Использует Redis для кэширования
   - Поддерживает фильтрацию, сортировку и пагинацию

---

## Используемые технологии

- **Python 3.11**
- **FastAPI**
- **Elasticsearch 8.x**
- **Redis**
- **PostgreSQL**
- **Docker / Docker Compose**
- **AsyncElasticsearch**
- **Pydantic v2**

---

## Запуск

`docker compose up --build`

---

---

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

3. **Сервис аутентификации**
   - Регистрация пользователя
   - Login (access + refresh токены)
   - Обновление access-токена
   - Logout
   - Logout всех устройств (через token_version)
   
   Подробнее см.: `auth/README.md`  

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
- **JWT (python-jose)**
- **SQLAlchemy (async)**
- **pytest**

---

## Запуск

`docker compose up --build`

---

---

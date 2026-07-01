# Online Cinema Microservices Platform

Backend-платформа онлайн-кинотеатра, построенная на микросервисной архитектуре.

Система включает:

- ETL сервис загрузки данных в Elasticsearch
- UGC pipeline: Kafka → ETL → ClickHouse
- UGC Content API (MongoDB)
- FastAPI API для контента
- Auth-сервис с JWT/OAuth2
- Redis caching и rate limiting
- Nginx gateway
- observability through OpenTelemetry and Jaeger

---

## Архитектура

Проект состоит из нескольких микросервисов, объединённых через Nginx gateway:

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


4. **Админ панель (Django Admin)**
    - Предоставляет интерфейс для управления данными фильмов, жанров и
      персоналий
    - Работает поверх существующей базы PostgreSQL (content schema)
    - Не управляет схемой базы данных (managed = False)
    - Использует встроенный Django Admin
    - Статические файлы собираются в volume и отдаются через Nginx

5. **UGC API**
    - Принимает пользовательские события
    - Публикует пользовательские события в Kafka

6  **UGC ETL**

- Читает события пользовательской активности из Kafka
- Обрабатывает события batch'ами
- Загружает данные в ClickHouse
- Коммитит Kafka offset только после успешной вставки

7  **UGC content API**

- Принимает оценки, рецензии и закладки
- Сохраняет всё в MongoDB
- Позволяет получать информацию по оценкам, рецензиям и закладкам

---

## Architecture diagrams

- [AS IS](docs/architecture/as_is.png)
- [TO BE](docs/architecture/to_be.png)

## OAuth авторизация

Auth-сервис поддерживает вход через Yandex OAuth2.

Flow:

1. Пользователь переходит на `/api/v1/auth/yandex/login`
2. Происходит redirect на Yandex OAuth
3. После успешной авторизации пользователь возвращается на callback endpoint
4. Auth-сервис создаёт локального пользователя и выдаёт JWT токены

Для защиты используется OAuth state parameter, сохраняемый в Redis.

---

## UGC API

Сервис принимает события пользовательской активности и отправляет их в Kafka.

### Поддерживаемые события

- `click`
- `page_view`
- `video_quality_changed`
- `video_completed`
- `search_filter_used`

#### Endpoint

```http
POST /api/v1/events
```

`Authorization` header optional:

- if JWT token is provided → `user_id` extracted from token
- if JWT token is absent → `anonymous_id` must be provided

Example request:

```bash
curl -X POST http://127.0.0.1/api/v1/events \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt_access_token>" \
  -d '{
    "event_type": "page_view",
    "anonymous_id": "f668e966-f64a-422f-abf8-5e39d4aa662a",
    "timestamp": "2026-05-22T12:00:00Z",
    "payload": {
      "page_url": "/movies/123",
      "movie_id": "123",
      "duration_seconds": 123,
      "video_quality": "full",
      "filter_name": "genre",
      "filter_value": "action"
    }
  }'
```

#### Health endpoints

- `GET /health` — liveness probe
- `GET /ready` — readiness probe (Kafka availability check)

#### Формат события:

```json
{
  "event_type": "page_view",
  "anonymous_id": "uuid",
  "timestamp": "ISO-8601 datetime",
  "payload": {}
}
```

#### Kafka

События публикуются в Kafka topic:
`events`

#### Проверка сообщений в Kafka:

```commandline
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic events \
  --from-beginning
```

---

#### Проверка данных в ClickHouse

```commandline
curl "http://localhost:8123" \
  --user default:password \
  -d "SELECT * FROM movies.events"
```

## UGC content API

Сервис хранения пользовательского контента.

### Возможности

- оценки фильмов;
- рецензии;
- лайки/дизлайки рецензий;
- закладки.

- FastAPI сервис
- MongoDB как основное хранилище
- Индексы для быстрого поиска
- CRUD API для оценок, рецензий и закладок

Для хранения оценок, рецензий и закладок выбран отдельный сервис
`ugc_content_api`.

Причины:

- существующий `ugc_api` отвечает за сбор событий пользовательского поведения и
  передачу их в Kafka;
- оценки, рецензии и закладки являются пользовательским контентом, который нужно
  читать синхронно и быстро;
- для нового сервиса требуется отдельное хранилище с индексами под сценарии
  чтения;
- требования к данным отличаются: события являются append-only потоком, а оценки
  и закладки нужно создавать, изменять и удалять;
- отдельный сервис проще независимо масштабировать и развивать.

Возможные недостатки:

- появляется ещё один сервис в инфраструктуре;
- усложняется локальный запуск;
- требуется отдельная настройка мониторинга, логирования и CI/CD.

## Graceful degradation

Административная панель не хранит локальные пароли пользователей.
Авторизация происходит через Auth API.

При недоступности Auth-сервиса:

- Movies API продолжает работать
- Admin panel остаётся доступной
- новые логины становятся невозможны

---

## Rate limiting

Проект использует двухуровневое ограничение запросов.

### Nginx level

Rate limiting реализован на уровне Nginx через `limit_req`.

Используются ограничения по IP:

- Auth API: 5 requests/sec
- Movies API: 10 requests/sec

При превышении лимита возвращается HTTP 429.

### Application level

Для Auth-сервиса дополнительно реализована защита от brute-force атак через
Redis:

- ограничение попыток login
- ограничение регистраций
- хранение счётчиков с TTL
- атомарные Redis операции через Lua scripts

---

## Observability

Используется OpenTelemetry + Jaeger.

Для каждого запроса:

- генерируется `X-Request-Id`
- request id прокидывается через Nginx
- трейсы отправляются в Jaeger через OTLP gRPC

---

## Безопасность

- JWT access/refresh токены
- Хеширование refresh токенов в БД (SHA-256)
- Хеширование паролей через bcrypt
- Logout всех устройств через token_version
- OAuth state validation
- Rate limiting через Redis
- Защита от brute-force login атак
- Защита от повторного использования OAuth state

---

## CI

Проект использует GitHub Actions.

Pipeline автоматически выполняет:

- Ruff (lint)
- Ruff formatter
- mypy
- pytest
- проверку на Python 3.10, 3.11 и 3.12
- отправку результата в Telegram


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
- **Django Admin**
- **Kafka**
- **ClickHouse**
- **Flask**
- **MongoDB**

---

## Запуск

```commandline
docker compose up --build
```

После запуска автоматически поднимаются:

- PostgreSQL
- Elasticsearch
- Redis
- MongoDB
- Kafka
- ClickHouse
- Auth API
- Movies API
- UGC API
- UGC Content API
- ETL сервисы
- Django Admin
- Nginx Gateway
---

## Доступные сервисы

- Movies API docs: http://localhost/movies/docs
- Auth API docs: http://localhost/auth/docs
- Django Admin: http://localhost/admin
- Jaeger UI: http://localhost:16686
- UGC content API docs: http://localhost/ugc-content/docs

---

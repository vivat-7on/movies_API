# Онлайн кинотеатр

Backend-платформа онлайн-кинотеатра, построенная на микросервисной архитектуре.

Система включает:

- ETL-сервис загрузки данных в Elasticsearch
- UGC pipeline: Kafka → ETL → ClickHouse
- UGC Content API (MongoDB)
- FastAPI API для контента
- Auth-сервис с JWT/OAuth2
- Profile-сервис
- Redis caching и rate limiting
- Notification-сервис для асинхронной отправки email-уведомлений
- Nginx Gateway
- observability through OpenTelemetry and Jaeger

---
## Возможности

- поиск и просмотр фильмов, жанров и персоналий;
- JWT-аутентификация и OAuth2 через Yandex;
- профили пользователей;
- оценки, рецензии и закладки;
- сбор пользовательских событий;
- асинхронные email-уведомления;
- административная панель;
- распределённая трассировка;
- кэширование и rate limiting.

---
## Сервисы

| Сервис          | Назначение                               |
|-----------------|------------------------------------------|
| Movies API      | API фильмов, жанров и персоналий         |
| Auth Service    | Аутентификация и авторизация              |
| Profile Service | Управление профилями пользователей        |
| UGC API         | Сбор пользовательских событий             |
| UGC Content API | Оценки, рецензии и закладки               |
| Notification    | Асинхронная отправка уведомлений          |
| ETL             | Перенос данных PostgreSQL → Elasticsearch |
| UGC ETL         | Перенос событий Kafka → ClickHouse        |
| Django Admin    | Административная панель                   |
```
                        Nginx Gateway
                              │
      ┌───────────────┬───────────────┬──────────────┐
      ▼               ▼               ▼              ▼
  Movies API      Auth API      Profile API    UGC Content
      │               │               │              │
      ▼               ▼               ▼              ▼
Elasticsearch     PostgreSQL      PostgreSQL      MongoDB

UGC API → Kafka → UGC ETL → ClickHouse

Notification API → PostgreSQL → RabbitMQ → Worker → SMTP

```

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
    - Предоставляет доступ к просмотру профилей пользователей
    - Использует общую базу PostgreSQL
    - Управляет собственными служебными таблицами Django
    - Модели контента и профилей подключены как внешние модели с `managed = False`
    - Использует встроенный Django Admin
    - Статические файлы собираются в volume и отдаются через Nginx

5. **UGC API**
    - Принимает пользовательские события
    - Публикует пользовательские события в Kafka

6. **UGC ETL**

    - Читает события пользовательской активности из Kafka
    - Обрабатывает события batch'ами
    - Загружает данные в ClickHouse
    - Коммитит Kafka offset только после успешной вставки

7. **UGC Content API**

    - Принимает оценки, рецензии и закладки
    - Сохраняет всё в MongoDB
    - Позволяет получать информацию по оценкам, рецензиям и закладкам

8. **Notification**

Состоит из двух компонентов.

### Notification API

- Принимает события от других сервисов
- Создаёт уведомление в PostgreSQL
- Публикует `notification_id` в RabbitMQ

### Worker

- Читает `notification_id` из RabbitMQ
- Получает уведомление из PostgreSQL
- Получает данные пользователя из Auth-service
- Рендерит email по шаблону
- Отправляет письмо пользователю
- Обновляет статус уведомления

9. **Profile API**

      - создание профиля
      - просмотр собственного профиля
      - изменение профиля
      - удаление профиля
      - валидация и нормализация номера телефона
      - JWT авторизация
      - интеграция с Django Admin

         Подробнее см.: `profile/README.md`

---

## Архитектурные схемы

- [AS IS](docs/architecture/as_is.png)
- [TO BE](docs/architecture/to_be.png)

## OAuth авторизация

Auth-сервис поддерживает вход через Yandex OAuth2.

Сценарий:

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

Заголовок `Authorization` не обязателен:

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

```bash
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic events \
  --from-beginning
```

---

#### Проверка данных в ClickHouse

```bash
curl "http://localhost:8123" \
  --user default:password \
  -d "SELECT * FROM movies.events"
```

## UGC Content API

Сервис хранения пользовательского контента.

### Возможности

- оценки фильмов;
- рецензии;
- лайки/дизлайки рецензий;
- закладки.

### Техническая реализация

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

### Эндпоинты

```
Базовый префикс API:

/api/v1/ugc-content

Bookmarks

PUT    /movies/{id}/bookmarks/me
DELETE /movies/{id}/bookmarks/me
GET    /bookmarks/me

Ratings

PUT    /movies/{id}/ratings/me
DELETE /movies/{id}/ratings/me
GET    /movies/{id}/ratings/me
GET    /movies/{id}/ratings/summary

Reviews

POST   /movies/{id}/reviews
PUT    /reviews/{id}
DELETE /reviews/{id}
GET    /reviews/{id}
GET    /movies/{id}/reviews

```

Повторное добавление закладки идемпотентно и не создаёт дубликат.
Список рецензий фильма поддерживает:

- пагинацию через `page` и `page_size`;
- сортировку;
- метаданные `total` и `pages`.

## Notification Service

Архитектура сервиса:

```
Other services
        │
        ▼
 Notification API
        │
        ▼
 PostgreSQL
        │
        ▼
 RabbitMQ
        │
        ▼
 Notification Worker
        │
        ├── Auth Service
        └── SMTP
```

### Supported events

- user_registered
- broadcast

Notification проходит следующие статусы:

- CREATED
- QUEUED
- PROCESSING
- SENT
- FAILED

### Внутренняя авторизация

Notification API предназначен для межсервисного взаимодействия и закрыт
service-to-service токеном.

Все запросы к эндпоинтам сервиса должны содержать заголовок:

```http
X-Service-Token: <service-token>
```

Токен задаётся через переменную окружения:

`NOTIFICATION_SERVICE_TOKEN=your-secret-token`

Если заголовок отсутствует, сервис вернёт 401 Unauthorized.
Если токен неверный, сервис вернёт 403 Forbidden.

---
## Profile service

### Эндпоинты

```
POST   /api/v1/profiles
GET    /api/v1/profiles/me
PATCH  /api/v1/profiles/me
DELETE /api/v1/profiles/me
```
Номер телефона нормализуется в формат E.164.

## Отказоустойчивость

Административная панель не хранит локальные пароли пользователей.
Авторизация происходит через Auth API.

При недоступности Auth-сервиса:

- Movies API продолжает работать;
- уже аутентифицированные администраторы могут продолжить работу до истечения Django-сессии;
- новые входы в административную панель становятся невозможны.

---

## Ограничение запросов

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

## Наблюдаемость

Используется OpenTelemetry + Jaeger.

Для каждого запроса:

- генерируется `X-Request-Id`
- request ID прокидывается через Nginx
- трейсы отправляются в Jaeger через OTLP gRPC

---

## Безопасность

- JWT access/refresh токены (RS256)
- Разделение приватного и публичного RSA-ключей
- Хеширование refresh токенов в БД (SHA-256)
- Хеширование паролей через bcrypt
- Logout всех устройств через token_version
- OAuth state validation
- Rate limiting через Redis
- Защита от brute-force login атак
- Защита от повторного использования OAuth state

---

## JWT

Проект использует асимметричную подпись JWT (RS256).

- Auth Service подписывает access и refresh токены приватным RSA-ключом.
- Остальные сервисы (Movies API, Profile API, UGC API, UGC Content API)
выполняют только проверку подписи с использованием публичного ключа.
- Приватный ключ присутствует только в Auth Service и не распространяется между сервисами.

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

**Backend:** Python 3.11, FastAPI, Flask, Django Admin, Pydantic v2  
**Databases:** PostgreSQL, MongoDB, ClickHouse, Elasticsearch  
**Messaging:** Kafka, RabbitMQ  
**Infrastructure:** Docker Compose, Nginx, Redis  
**Observability:** OpenTelemetry, Jaeger  
**Testing and quality:** pytest, mypy, Ruff, flake8  
Security: JWT (RS256), OAuth2, bcrypt

---

## Запуск

Также необходимо создать RSA-пару ключей для подписи JWT и разместить её в каталоге:

```text
secrets/jwt/
├── private.pem
└── public.pem
```

Пример генерации:

```bash
openssl genpkey -algorithm RSA -out secrets/jwt/private.pem -pkeyopt rsa_keygen_bits:2048

openssl rsa \
  -pubout \
  -in secrets/jwt/private.pem \
  -out secrets/jwt/public.pem
```

```bash
docker compose up --build
```
Перед запуском необходимо создать `.env`-файлы сервисов на основе соответствующих `.env.example`.
При запуске Docker Compose Alembic-миграции Profile Service и Notification Service применяются автоматически до старта API.
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
- RabbitMQ

---

## Сквозной пользовательский сценарий

1. Пользователь проходит аутентификацию и получает JWT.
2. Создаёт и обновляет профиль.
3. Добавляет фильм в закладки.
4. Ставит фильму оценку.
5. Создаёт рецензию.
6. Администратор видит профиль пользователя в Django Admin.

## Доступные сервисы

- Movies API docs: http://localhost/movies/docs
- Auth API docs: http://localhost/auth/docs
- Django Admin: http://localhost/admin
- Jaeger UI: http://localhost:16686
- UGC content API docs: http://localhost/ugc-content/docs
- Profile API docs: http://localhost/profiles/docs

---

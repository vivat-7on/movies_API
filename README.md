# Online Cinema Microservices Platform

Backend-платформа онлайн-кинотеатра, построенная на микросервисной архитектуре.

Система включает:
- ETL сервис загрузки данных в Elasticsearch
- FastAPI API для контента
- Auth-сервис с JWT/OAuth2
- Redis caching и rate limiting
- Nginx gateway
- observability через OpenTelemetry и Jaeger

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
   - Предоставляет интерфейс для управления данными фильмов, жанров и персоналий
   - Работает поверх существующей базы PostgreSQL (content schema)
   - Не управляет схемой базы данных (managed = False)
   - Использует встроенный Django Admin
   - Статические файлы собираются в volume и отдаются через Nginx
   
---

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
Пример запроса:
```commandline
curl -X POST http://127.0.0.1/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "page_view",
    "user_id": "f668e966-f64a-422f-abf8-5e39d4aa662a",
    "timestamp": "2026-05-22T12:00:00Z",
    "payload": {
      "page_url": "/movies/123",
      "duration_seconds": 42
    }
  }'
```
#### Формат события:

```json
{
  "event_type": "page_view",
  "user_id": "uuid",
  "timestamp": "ISO-8601 datetime",
  "payload": {}
}
```
#### Kafka

События публикуются в Kafka topic:
`events`

Проверка сообщений в Kafka:
```commandline
docker exec -it kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic events \
  --from-beginning
```
---

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

Для Auth-сервиса дополнительно реализована защита от brute-force атак через Redis:

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

---

## Запуск

`docker compose up --build`

---

## Доступные сервисы

- Movies API docs: http://localhost/movies/docs
- Auth API docs: http://localhost/auth/docs
- Django Admin: http://localhost/admin
- Jaeger UI: http://localhost:16686

---

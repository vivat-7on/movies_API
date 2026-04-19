# Auth Service

Сервис аутентификации и авторизации пользователей с поддержкой JWT и RBAC.

---

## Функционал

### Аутентификация

- Регистрация пользователя
- Login (access + refresh токены)
- Обновление access-токена
- Logout
- Logout всех устройств (через token_version)

### Пользователь

- Получение текущего пользователя (/me)

### Роли (RBAC)

- Создание роли
- Получение списка ролей
- Обновление роли
- Удаление роли
- Назначение роли пользователю
- Удаление роли у пользователя
- Проверка прав через require_roles

---

## Стек

- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- JWT (python-jose)
- pytest

---

## Авторизация

- Access token (JWT)
- Refresh token (хранится в БД в хэшированном виде)
- Logout всех устройств через `token_version`

---

## API

### Auth

- POST /auth/login
- POST /auth/registration
- POST /auth/refresh
- POST /auth/logout
- POST /auth/logout-all
- GET /auth/me

### Roles

- POST /roles
- GET /roles
- PATCH /roles/{role_id}
- DELETE /roles/{role_id}

### User Roles

- POST /users/{user_id}/roles/{role_id}
- DELETE /users/{user_id}/roles/{role_id}

---

### Ошибки

- 401 — невалидный токен / нет токена
- 403 — недостаточно прав
- 404 — сущность не найдена
- 400 — ошибка валидации / дубликат

---

## Запуск

```bash
docker compose up --build
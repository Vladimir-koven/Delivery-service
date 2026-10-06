# Delivery Service

Сервис доставки на FastAPI: управление курьерами, заказами и пользователями.

## Стек

- **Python 3.12**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.x (async)** + **asyncpg** — ORM
- **PostgreSQL 16** — БД
- **Alembic** — миграции
- **Pydantic v2** + **pydantic-settings** — схемы и настройки
- **python-jose** — JWT
- **passlib** + **bcrypt** — хеширование паролей
- **python-multipart** — form-data для логина
- **email-validator** — валидация email
- **Poetry** — управление зависимостями
- **Docker** + **Docker Compose** — контейнеризация
- **pytest** + **httpx** — тесты
- **ruff**, **mypy**, **bandit**, **pre-commit** — качество кода

## Архитектура
HTTP → Routing → Service → Repository → PostgreSQL
↓ ↓ ↓
Schemas Exceptions SQLAlchemy


**Слои:**
- **Routing** — HTTP-эндпоинты, валидация запросов через Pydantic.
- **Service** — бизнес-логика, доменные правила.
- **Repository** — работа с БД через SQLAlchemy.
- **Schemas** — Pydantic-модели для API.
- **Models** — SQLAlchemy-модели для БД.
- **Core** — security (JWT, хеширование паролей).
- **Exceptions** — доменные исключения + единые handlers.

## Возможности

### Курьеры
- **CRUD**: создание, чтение, обновление, удаление.
- **Статусы**: `available`, `busy`, `offline`.
- **Фильтр** по статусу.
- **CUD** требует **авторизации** (`GET` — публичный).

### Заказы
- **CRUD**: создание, чтение, обновление, удаление.
- **Статусы**: `created`, `assigned`, `in_progress`, `delivered`, `cancelled`.
- **Назначение** курьера на заказ.
- **Смена** статуса с валидацией переходов.
- **Автоматическое** освобождение курьера при `delivered`/`cancelled`.
- **CUD** требует **авторизации** (`GET` — публичный).

### Аутентификация (JWT)
- **Регистрация** пользователей.
- **Логин** по email и паролю.
- **JWT access token** (HS256, 30 минут).
- **Защита** CUD-эндпоинтов через `OAuth2PasswordBearer`.
- **Роли**: `admin`, `user`, `courier` (пока по умолчанию — `user`).


## Структура проекта
delivery-service/
├── src/delivery/
│ ├── main.py # FastAPI app
│ ├── config.py # Настройки (App, DB, JWT)
│ ├── depends.py # DI-зависимости
│ ├── core/
│ │ └── security.py # Хеширование паролей, JWT
│ ├── db/ # БД: engine, session, Base
│ ├── models/ # SQLAlchemy-модели
│ │ ├── courier.py
│ │ ├── order.py
│ │ └── user.py
│ ├── schemas/ # Pydantic-схемы
│ │ ├── courier.py
│ │ ├── order.py
│ │ └── user.py
│ ├── repositories/ # Работа с БД
│ │ ├── courier.py
│ │ ├── order.py
│ │ └── user.py
│ ├── services/ # Бизнес-логика
│ │ ├── auth.py
│ │ ├── courier.py
│ │ └── order.py
│ ├── routing/ # HTTP-эндпоинты
│ │ ├── auth.py
│ │ ├── couriers.py
│ │ ├── health.py
│ │ └── orders.py
│ └── exceptions/ # Доменные исключения + handlers
│ ├── auth.py
│ ├── base.py
│ ├── courier.py
│ ├── handlers.py
│ └── order.py
├── migrations/ # Alembic
├── tests/ # pytest
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── init-db.sql # Создание test DB
├── pyproject.toml
└── Makefile


## Требования

- **Docker Desktop** (для запуска БД и приложения)
- **Python 3.12**
- **Poetry 2.x** (для локальной разработки)
- **Make** (опционально, для удобных команд)

## Быстрый старт (Docker)

# Клонировать репозиторий
git clone git@github.com:Vladimir-koven/Delivery-service.git
cd Delivery-service

# Создать .env из шаблона
cp .env.example .env

# Сгенерировать JWT_SECRET (64 символа)
poetry run python -c "import secrets; print(secrets.token_urlsafe(64))"
# Вставь в .env: JWT_SECRET=<полученная_строка>

# Поднять приложение и БД
docker compose up -d --build

# Проверить статус
docker compose ps

# Приложение будет доступно:
API: http://localhost:8000
Swagger: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc


# Миграции применяются автоматически при старте через entrypoint.sh.


# Остановка
docker compose down        # остановить, сохранить данные
docker compose down -v     # остановить и удалить volume с БД


## Установка 
# Установить зависимости
poetry install

# Активировать venv
poetry shell

# или
.\.venv\Scripts\Activate.ps1   # Windows


## БД
# Поднять Postgres
docker compose up -d db

# Применить миграции
poetry run alembic upgrade head

## Запуск приложения
poetry run uvicorn delivery.main:app --reload --port 8000


## Команды Makefile
make install	Установить зависимости
make lint	    ruff check --fix
make fmt	    ruff format
make type	    mypy
make security	bandit
make check	    Полная проверка (ruff + mypy + bandit)
make fix	    Авто-фикс (lint + format)
make migrate	alembic upgrade head
make reset-db	Сбросить БД + миграции
make test	    Запустить тесты
make test-cov	Тесты с покрытием
make clean	    Очистить кэши


## Тесты
# Все тесты
poetry run pytest

# С покрытием
poetry run pytest --cov=delivery --cov-report=term-missing

# Конкретный файл(пример)
poetry run pytest tests/test_couriers_api.py

Тестовая БД: delivery_test создаётся автоматически (init-db.sql в Docker, отдельный шаг в CI)


## Формат ошибок
Все доменные ошибки возвращаются в едином формате:

Коды:

Код	Статус	Когда
courier_not_found(404)	    Курьер не найден
order_not_found(404)	      Заказ не найден
order_status_transition_error(409)	Недопустимый переход статуса
email_already_exists(409)	  Email уже зарегистрирован
invalid_credentials(401)	  Неверный email или пароль
invalid_token(401)	        Невалидный или истёкший JWT
inactive_user(403)	        Пользователь деактивирован

## Миграции
# Создать миграцию
poetry run alembic revision --autogenerate -m "add field X"

# Применить
poetry run alembic upgrade head

# Откатить последнюю
poetry run alembic downgrade -1

# Откатить всё
poetry run alembic downgrade base

# Текущая версия
poetry run alembic current


## Аутентификация (JWT)
# Регистрация
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "full_name": "User", "password": "strong_password"}'

# Логин (получить токен)
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password&username=user@example.com&password=strong_password"
  
# Создать курьера(необходим токен)
curl -X POST http://localhost:8000/couriers \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иван Петров",
    "phone": "+79991234567",
    "status": "available"
  }'

# Создать заказ (с токеном)
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Алиса",
    "customer_phone": "+79992222222",
    "address": "ул. Ленина, д. 1",
    "total_amount": 1500.50
  }'

# Назначить курьера на заказ
curl -X POST http://localhost:8000/orders/{order_id}/assign \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"courier_id": "{courier_id}"}'

# Публичный список курьеров
curl http://localhost:8000/couriers
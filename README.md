# Delivery Service
Сервис доставки на FastAPI: управление курьерами и заказами.


## Структура проекта
delivery-service/
├── src/delivery/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Настройки
│   ├── depends.py           # DI-зависимости
│   ├── db/                  # БД: engine, session, Base
│   ├── models/              # SQLAlchemy-модели
│   ├── schemas/             # Pydantic-схемы
│   ├── repositories/        # Работа с БД
│   ├── services/            # Бизнес-логика
│   ├── routing/             # HTTP-эндпоинты
│   └── exceptions/          # Доменные исключения + handlers
├── migrations/              # Alembic
├── tests/                   # pytest
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh
├── pyproject.toml
└── Makefile


## Стек
- **Python 3.12**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.x (async)** + **asyncpg** — ORM
- **PostgreSQL 16** — БД
- **Alembic** — миграции
- **Pydantic v2** + **pydantic-settings** — схемы и настройки
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
- **Exceptions** — доменные исключения + единые handlers.

## Возможности
- **Курьеры**: CRUD, статусы (`available`, `busy`, `offline`).
- **Заказы**: CRUD, статусы (`created`, `assigned`, `in_progress`, `delivered`, `cancelled`).
- **Назначение курьера** на заказ с проверкой доступности.
- **Смена статуса** заказа с валидацией переходов.
- **Автоматическое освобождение** курьера при `delivered`/`cancelled`.
- **Единый формат ошибок** через exception handlers.

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


## Формат ошибок
Все доменные ошибки возвращаются в едином формате:

json
{
  "error": {
    "code": "courier_not_found",
    "message": "Courier ... not found"
  }
}

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


## API — примеры
# Создать курьера
curl -X POST http://localhost:8000/couriers \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Иван Петров",
    "phone": "+79991234567",
    "status": "available"
  }'

# Создать заказ
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Алиса",
    "customer_phone": "+79992222222",
    "address": "ул. Ленина, д. 1",
    "total_amount": 1500.50
  }'

# Назначить курьера на заказ
curl -X POST http://localhost:8000/orders/{order_id}/assign \
  -H "Content-Type: application/json" \
  -d '{"courier_id": "{courier_id}"}'
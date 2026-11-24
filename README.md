# Каталог товаров

Учебная КТ по Docker и CI/CD на основе каталога из работы по FastAPI. Схема товара и учебные товары перенесены из каталога. Приложение читает данные из PostgreSQL. Маршрут `/health` проверяет PostgreSQL и Redis.

## Локальный запуск

```sh
docker compose up --build
```

- Swagger UI доступен на http://localhost:8000/docs
- ReDoc доступен на http://localhost:8000/redoc
- Состояние приложения доступно на http://localhost:8000/health

При запуске приложение создаёт таблицы и добавляет учебные данные. Повторный запуск сохраняет их в томе `postgres_data`. В `.env.docker` используются имена контейнерных сервисов `db` и `redis` как адреса внутри сети Compose.

## Маршруты

| Метод | Адрес | Результат |
| --- | --- | --- |
| GET | `/products` | Список товаров с фильтром `category_id` |
| GET | `/products/{product_id}` | Один товар по ID |
| GET | `/categories` | Список категорий |
| GET | `/categories/{category_id}` | Одна категория |
| GET | `/categories/{category_id}/products` | Товары категории |
| GET | `/health` | Проверка доступности PostgreSQL и Redis |

## Проверки

GitHub Actions запускает `python -m pytest -v` при push в `main`. Для тестов workflow поднимает PostgreSQL и Redis. После тестов он запускает проект через Compose и проверяет `/health` и `/docs`.

## Railway

Приложение собирается из `Dockerfile`. В сервисе приложения задайте `DATABASE_URL` и `REDIS_URL` как ссылки на внутренние переменные сервисов PostgreSQL и Redis. Проверка готовности настроена через `/health`. Swagger открывается на публичном адресе приложения по пути `/docs`.

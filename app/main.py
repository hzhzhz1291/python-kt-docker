import asyncio
import os
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from redis import Redis
from redis.exceptions import RedisError
from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.database import get_db, init_database, make_engine
from app.models import Category, Product


class CategoryView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор категории", examples=[1])
    name: str = Field(description="Название категории", examples=["Электроника"])


class ProductView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор товара", examples=[1])
    name: str = Field(description="Название товара", examples=["Кабель USB-C"])
    price: Decimal = Field(description="Цена в рублях", examples=["990.00"])
    category_id: int = Field(description="Идентификатор категории товара", examples=[1])


@asynccontextmanager
async def lifespan(application: FastAPI):
    engine = make_engine(os.environ["DATABASE_URL"])
    try:
        with Redis.from_url(os.environ["REDIS_URL"], socket_connect_timeout=2,
                            socket_timeout=2) as redis:
            for attempt in range(1, 9):
                try:
                    await run_in_threadpool(init_database, engine)
                    break
                except OperationalError:
                    if attempt == 8:
                        raise
                    await asyncio.sleep(2)
            application.state.engine = engine
            application.state.redis = redis
            yield
    finally:
        engine.dispose()


app = FastAPI(
    title="Каталог товаров",
    description="Учебный API для просмотра товаров и категорий с данными из PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan,
)

Db = Annotated[Session, Depends(get_db)]
PositiveId = Annotated[int, Path(ge=1)]


@app.get("/health", tags=["Состояние"], summary="Проверить приложение")
def health(request: Request, db: Db):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="PostgreSQL недоступен") from exc
    try:
        request.app.state.redis.ping()
    except RedisError as exc:
        raise HTTPException(status_code=503, detail="Redis недоступен") from exc
    return {"status": "ok", "database": "ok", "redis": "ok"}


@app.get("/products", response_model=list[ProductView], tags=["Товары"], summary="Список товаров",
         description="Возвращает товары по возрастанию ID. Параметр category_id ограничивает список выбранной категорией.")
def products(db: Db, category_id: Annotated[int | None, Query(ge=1)] = None):
    statement = select(Product).order_by(Product.id)
    if category_id is not None:
        statement = statement.where(Product.category_id == category_id)
    return db.scalars(statement).all()


@app.get("/products/{product_id}", response_model=ProductView, tags=["Товары"], summary="Получить товар",
         description="Если товара с таким идентификатором нет, возвращает HTTP 404.")
def product(product_id: PositiveId, db: Db):
    result = db.get(Product, product_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return result


@app.get("/categories", response_model=list[CategoryView], tags=["Категории"], summary="Список категорий")
def categories(db: Db):
    return db.scalars(select(Category).order_by(Category.id)).all()


@app.get("/categories/{category_id}", response_model=CategoryView, tags=["Категории"], summary="Получить категорию")
def category(category_id: PositiveId, db: Db):
    result = db.get(Category, category_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Категория не найдена")
    return result


@app.get("/categories/{category_id}/products", response_model=list[ProductView], tags=["Категории"],
         summary="Товары категории",
         description="Возвращает товары существующей категории. Для неизвестной категории возвращает HTTP 404.")
def category_products(category_id: PositiveId, db: Db):
    category(category_id, db)
    return products(db, category_id)

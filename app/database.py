from collections.abc import Iterator
from decimal import Decimal

from fastapi import Request
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Base, Category, Product


def make_engine(url: str) -> Engine:
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            url = "postgresql+psycopg://" + url.removeprefix(prefix)
            break
    return create_engine(url, pool_pre_ping=True, pool_size=3, max_overflow=1,
                         connect_args={"connect_timeout": 5})


def init_database(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(800173)"))
        Base.metadata.create_all(connection)
        connection.execute(insert(Category).values([
            {"id": 1, "name": "Электроника"},
            {"id": 2, "name": "Канцелярия"},
        ]).on_conflict_do_nothing())
        connection.execute(insert(Product).values([
            {"id": 1, "name": "Кабель USB-C", "price": Decimal("990.00"), "category_id": 1},
            {"id": 2, "name": "Наушники", "price": Decimal("2490.00"), "category_id": 1},
            {"id": 3, "name": "Блокнот", "price": Decimal("190.00"), "category_id": 2},
        ]).on_conflict_do_nothing())


def get_db(request: Request) -> Iterator[Session]:
    with Session(request.app.state.engine) as session:
        yield session

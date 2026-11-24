from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Идентификатор товара", examples=[1])
    name: str = Field(description="Название товара", examples=["Кабель USB-C"])
    price: Decimal = Field(description="Цена в рублях", examples=["990.00"])
    category_id: int = Field(description="Идентификатор категории", examples=[1])


PRODUCTS = (
    ProductView(id=1, name="Кабель USB-C", price=Decimal("990.00"), category_id=1),
    ProductView(id=2, name="Наушники", price=Decimal("2490.00"), category_id=1),
    ProductView(id=3, name="Блокнот", price=Decimal("190.00"), category_id=2),
)

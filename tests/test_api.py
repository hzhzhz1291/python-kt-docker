import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client


def test_health_checks_database_and_redis(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok", "redis": "ok"}


def test_product_list_reads_seeded_database(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [1, 2, 3]


def test_filter_products_by_category(client):
    response = client.get("/products", params={"category_id": 2})
    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [3]


def test_get_product_and_handle_missing_id(client):
    product = client.get("/products/1")
    assert product.status_code == 200
    assert product.json()["price"] == "990.00"
    assert client.get("/products/999").status_code == 404


def test_get_categories_and_related_products(client):
    categories = client.get("/categories")
    assert categories.status_code == 200
    assert [category["id"] for category in categories.json()] == [1, 2]
    assert client.get("/categories/1").json()["name"] == "Электроника"
    response = client.get("/categories/1/products")
    assert response.status_code == 200
    assert [product["id"] for product in response.json()] == [1, 2]
    assert client.get("/categories/999/products").status_code == 404


def test_swagger_and_redoc(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/redoc").status_code == 200
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Каталог товаров"

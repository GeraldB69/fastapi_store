from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.models.products import Category, Product
from app.routers.products import products_db
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_products_db():
    """Reset the in-memory store to a known state before each test."""
    products_db.clear()
    products_db.extend([
        Product(id=uuid4(), name="Laptop", price=Decimal("999.99"), stock=5, category=Category.electronics),
        Product(id=uuid4(), name="T-shirt", price=Decimal("19.99"), stock=20, category=Category.clothing),
        Product(id=uuid4(), name="Old item", price=Decimal("9.99"), stock=0, category=Category.other, is_active=False),
    ])
    yield
    products_db.clear()


class TestGetProducts:
    def test_returns_all_products(self):
        response = client.get("/api/v1/products")

        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_active_only_filter_excludes_inactive(self):
        response = client.get("/api/v1/products?active_only=true")

        data = response.json()
        assert len(data) == 2
        assert all(p["is_active"] for p in data)

    def test_response_shape(self):
        data = client.get("/api/v1/products").json()

        assert all(
            {"id", "name", "price", "stock", "category", "is_active"} <= p.keys()
            for p in data
        )


class TestGetProduct:
    def test_returns_product_by_id(self):
        product_id = str(products_db[0].id)

        response = client.get(f"/api/v1/products/{product_id}")

        assert response.status_code == 200
        assert response.json()["id"] == product_id

    def test_unknown_id_returns_404(self):
        response = client.get(f"/api/v1/products/{uuid4()}")

        assert response.status_code == 404


class TestCreateProduct:
    def test_creates_product_and_returns_201(self):
        payload = {"name": "New Phone", "price": "599.99", "stock": 10, "category": "electronics"}

        response = client.post("/api/v1/products", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Phone"
        assert data["is_active"] is True  # default

    def test_price_zero_returns_422(self):
        payload = {"name": "Free item", "price": "0", "stock": 5, "category": "other"}

        response = client.post("/api/v1/products", json=payload)

        assert response.status_code == 422

    def test_negative_stock_returns_422(self):
        payload = {"name": "Item", "price": "9.99", "stock": -1, "category": "other"}

        response = client.post("/api/v1/products", json=payload)

        assert response.status_code == 422


class TestPatchProduct:
    def test_updates_only_sent_fields(self):
        product_id = str(products_db[0].id)
        original_name = products_db[0].name

        response = client.patch(f"/api/v1/products/{product_id}", json={"stock": 99})

        assert response.status_code == 200
        data = response.json()
        assert data["stock"] == 99
        assert data["name"] == original_name  # unchanged

    def test_can_deactivate_via_patch(self):
        product_id = str(products_db[0].id)

        response = client.patch(f"/api/v1/products/{product_id}", json={"is_active": False})

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_unknown_id_returns_404(self):
        response = client.patch(f"/api/v1/products/{uuid4()}", json={"stock": 1})

        assert response.status_code == 404


class TestReplaceProduct:
    def test_replaces_all_fields(self):
        product_id = str(products_db[0].id)
        payload = {"name": "Replaced", "price": "1.99", "stock": 1, "category": "food", "is_active": True}

        response = client.put(f"/api/v1/products/{product_id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Replaced"
        assert data["id"] == product_id  # id unchanged

    def test_unknown_id_returns_404(self):
        payload = {"name": "X", "price": "1.00", "stock": 1, "category": "other", "is_active": True}

        response = client.put(f"/api/v1/products/{uuid4()}", json=payload)

        assert response.status_code == 404


class TestSoftDeleteProduct:
    def test_returns_204(self):
        product_id = str(products_db[0].id)

        response = client.delete(f"/api/v1/products/{product_id}")

        assert response.status_code == 204
        assert response.content == b""  # no body

    def test_product_still_exists_after_soft_delete(self):
        """Unlike hard delete, the product stays in the store — just deactivated."""
        product_id = str(products_db[0].id)
        client.delete(f"/api/v1/products/{product_id}")

        response = client.get(f"/api/v1/products/{product_id}")

        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_soft_deleted_product_excluded_from_active_filter(self):
        product_id = str(products_db[0].id)
        client.delete(f"/api/v1/products/{product_id}")

        active = client.get("/api/v1/products?active_only=true").json()

        assert all(p["id"] != product_id for p in active)

    def test_unknown_id_returns_404(self):
        response = client.delete(f"/api/v1/products/{uuid4()}")

        assert response.status_code == 404

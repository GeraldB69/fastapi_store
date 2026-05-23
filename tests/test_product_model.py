from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models.products import Category, CreateProduct, Product, UpdateProduct


@pytest.fixture
def product_id() -> UUID:
    return uuid4()


@pytest.fixture
def valid_product_kwargs(product_id: UUID) -> dict:
    return {
        "id": product_id,
        "name": "Laptop Pro 15",
        "description": "High-performance laptop",
        "price": Decimal("1299.99"),
        "stock": 10,
        "category": Category.electronics,
    }


class TestProduct:
    def test_create_valid(self, valid_product_kwargs: dict) -> None:
        product = Product(**valid_product_kwargs)

        assert product.name == "Laptop Pro 15"
        assert product.price == Decimal("1299.99")
        assert product.stock == 10
        assert product.category is Category.electronics
        assert product.is_active is True  # valeur par défaut

    def test_description_is_optional(self, product_id: UUID) -> None:
        product = Product(
            id=product_id,
            name="T-shirt",
            price=Decimal("19.99"),
            stock=100,
            category=Category.clothing,
        )

        assert product.description is None

    def test_is_active_defaults_to_true(self, valid_product_kwargs: dict) -> None:
        product = Product(**valid_product_kwargs)

        assert product.is_active is True

    def test_can_create_inactive_product(self, product_id: UUID) -> None:
        product = Product(
            id=product_id,
            name="Old jacket",
            price=Decimal("49.00"),
            stock=0,
            category=Category.clothing,
            is_active=False,
        )

        assert product.is_active is False

    def test_price_rejects_zero(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            Product(
                id=product_id,
                name="Free item",
                price=Decimal("0"),
                stock=5,
                category=Category.other,
            )

    def test_price_rejects_negative(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            Product(
                id=product_id,
                name="Bad item",
                price=Decimal("-10.00"),
                stock=5,
                category=Category.other,
            )

    def test_stock_rejects_negative(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            Product(
                id=product_id,
                name="Item",
                price=Decimal("9.99"),
                stock=-1,
                category=Category.other,
            )

    def test_stock_zero_is_valid(self, product_id: UUID) -> None:
        product = Product(
            id=product_id,
            name="Out of stock item",
            price=Decimal("9.99"),
            stock=0,
            category=Category.other,
        )

        assert product.stock == 0

    def test_invalid_category_raises(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            Product(
                id=product_id,
                name="Item",
                price=Decimal("9.99"),
                stock=5,
                category="unknown_category",
            )

    def test_coerces_string_category(self, product_id: UUID) -> None:
        product = Product(
            id=product_id,
            name="Ball",
            price=Decimal("29.99"),
            stock=20,
            category="sport",
        )

        assert product.category is Category.sport

    def test_roundtrip(self, valid_product_kwargs: dict) -> None:
        product = Product(**valid_product_kwargs)
        restored = Product.model_validate(product.model_dump())

        assert restored == product

    def test_patch_with_model_copy(self, valid_product_kwargs: dict) -> None:
        product = Product(**valid_product_kwargs)
        update = UpdateProduct(stock=0, is_active=False)

        patched = product.model_copy(update=update.model_dump(exclude_unset=True))

        assert patched.stock == 0
        assert patched.is_active is False
        assert patched.name == product.name  # champs non envoyés inchangés
        assert patched.price == product.price

    def test_soft_delete_via_patch(self, valid_product_kwargs: dict) -> None:
        """Le soft delete = PATCH is_active=False, le produit reste en base."""
        product = Product(**valid_product_kwargs)
        deactivated = product.model_copy(update={"is_active": False})

        assert deactivated.id == product.id  # même id, toujours en base
        assert deactivated.is_active is False

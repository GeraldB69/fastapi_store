from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models.products import Category, ProductCreate, ProductResponse, ProductUpdate


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
        "category": Category.ELECTRONICS,
    }


class TestProduct:
    def test_create_valid(self, valid_product_kwargs: dict) -> None:
        product = ProductResponse(**valid_product_kwargs)

        assert product.name == "Laptop Pro 15"
        assert product.price == Decimal("1299.99")
        assert product.stock == 10
        assert product.category is Category.ELECTRONICS
        assert product.is_active is False  # inactive by default

    def test_description_accepts_none(self, product_id: UUID) -> None:
        product = ProductResponse(
            id=product_id,
            name="T-shirt",
            description=None,
            price=Decimal("19.99"),
            stock=100,
            category=Category.CLOTHING,
        )

        assert product.description is None

    def test_description_is_required(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            ProductResponse(
                id=product_id,
                name="T-shirt",
                price=Decimal("19.99"),
                stock=100,
                category=Category.CLOTHING,
            )

    def test_is_active_defaults_to_false(self, valid_product_kwargs: dict) -> None:
        product = ProductResponse(**valid_product_kwargs)

        assert product.is_active is False

    def test_can_create_active_product(self, product_id: UUID) -> None:
        product = ProductResponse(
            id=product_id,
            name="Featured item",
            description="On sale now",
            price=Decimal("49.00"),
            stock=20,
            category=Category.CLOTHING,
            is_active=True,
        )

        assert product.is_active is True

    def test_price_rejects_zero(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            ProductResponse(
                id=product_id,
                name="Free item",
                description=None,
                price=Decimal("0"),
                stock=5,
                category=Category.OTHER,
            )

    def test_price_rejects_negative(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            ProductResponse(
                id=product_id,
                name="Bad item",
                description=None,
                price=Decimal("-10.00"),
                stock=5,
                category=Category.OTHER,
            )

    def test_stock_rejects_negative(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            ProductResponse(
                id=product_id,
                name="Item",
                description=None,
                price=Decimal("9.99"),
                stock=-1,
                category=Category.OTHER,
            )

    def test_stock_zero_is_valid(self, product_id: UUID) -> None:
        product = ProductResponse(
            id=product_id,
            name="Out of stock item",
            description=None,
            price=Decimal("9.99"),
            stock=0,
            category=Category.OTHER,
        )

        assert product.stock == 0

    def test_invalid_category_raises(self, product_id: UUID) -> None:
        with pytest.raises(ValidationError):
            ProductResponse(
                id=product_id,
                name="Item",
                description=None,
                price=Decimal("9.99"),
                stock=5,
                category="unknown_category",
            )

    def test_coerces_string_category(self, product_id: UUID) -> None:
        product = ProductResponse(
            id=product_id,
            name="Ball",
            description="Basketball",
            price=Decimal("29.99"),
            stock=20,
            category="sport",
        )

        assert product.category is Category.SPORT

    def test_roundtrip(self, valid_product_kwargs: dict) -> None:
        product = ProductResponse(**valid_product_kwargs)
        restored = ProductResponse.model_validate(product.model_dump())

        assert restored == product

    def test_patch_with_model_copy(self, valid_product_kwargs: dict) -> None:
        product = ProductResponse(**valid_product_kwargs)
        update = ProductUpdate(stock=0, is_active=True)

        patched = product.model_copy(update=update.model_dump(exclude_unset=True))

        assert patched.stock == 0
        assert patched.is_active is True
        assert patched.name == product.name  # unchanged fields
        assert patched.price == product.price

    def test_soft_delete_via_patch(self, valid_product_kwargs: dict) -> None:
        """Soft delete = PATCH is_active=False; product stays in the store."""
        product = ProductResponse(**valid_product_kwargs, is_active=True)
        deactivated = product.model_copy(update={"is_active": False})

        assert deactivated.id == product.id  # same id, still in store
        assert deactivated.is_active is False

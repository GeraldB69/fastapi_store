from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from app.models.products import (
    Category,
    ProductCreate,
    ProductResponse,
    ProductReplace,
    ProductUpdate,
)

import logging

logger = logging.getLogger("uvicorn.error")

# APIRouter groups all routes for a domain under a shared prefix and tag.
# Equivalent of Django's include() in urls.py.
router = APIRouter(prefix="/api/v1/products", tags=["Product"])

# In-memory store — no database yet.
products_db: List[ProductResponse] = [
    ProductResponse(
        id=uuid4(),
        name="Laptop Pro 15",
        description="High-performance laptop",
        price=Decimal("1299.99"),
        stock=10,
        category=Category.ELECTRONICS,
    ),
    ProductResponse(
        id=uuid4(),
        name="Running Shoes X",
        description="Lightweight running shoes",
        price=Decimal("89.90"),
        stock=50,
        category=Category.SPORT,
    ),
    ProductResponse(
        id=uuid4(),
        name="Winter Jacket",
        description=None,
        price=Decimal("149.00"),
        stock=0,
        category=Category.CLOTHING,
        is_active=False,  # out of stock → deactivated
    ),
]


def _find_product_index(product_id: UUID) -> int | None:
    """Return the index in products_db, or None if not found."""
    for index, product in enumerate(products_db):
        if product.id == product_id:
            return index
    return None


# --- Collection ---


@router.get("", response_model=List[ProductResponse])
def get_products(active_only: bool = False):
    """
    List all products.
    Optional query param ?active_only=true to return only active products.
    """
    logger.info("GET /api/v1/products - active_only=%s", active_only)
    if active_only:
        return [p for p in products_db if p.is_active]
    return products_db


@router.post("", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate):
    """Create a product. The id is server-generated."""
    new_product = ProductResponse(id=uuid4(), **payload.model_dump())
    products_db.append(new_product)
    logger.info("POST /api/v1/products - created id=%s", new_product.id)
    return new_product


# --- Single resource by id ---


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    responses={404: {"description": "Product not found"}},
)
def get_product(product_id: UUID):
    """Retrieve a product by its UUID."""
    index = _find_product_index(product_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return products_db[index]


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
    responses={404: {"description": "Product not found"}},
)
def patch_product(product_id: UUID, payload: ProductUpdate):
    """
    Partial update (PATCH).
    Can be used to deactivate a product (is_active=false) without deleting it.
    """
    index = _find_product_index(product_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    products_db[index] = products_db[index].model_copy(
        update=payload.model_dump(exclude_unset=True),
    )
    logger.info("PATCH /api/v1/products/%s", product_id)
    return products_db[index]


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    responses={404: {"description": "Product not found"}},
)
def replace_product(product_id: UUID, payload: ProductReplace):
    """Full replacement (PUT). The id comes from the URL only."""
    index = _find_product_index(product_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    products_db[index] = ProductResponse(id=product_id, **payload.model_dump())
    logger.info("PUT /api/v1/products/%s", product_id)
    return products_db[index]


@router.delete(
    "/{product_id}",
    status_code=204,
    responses={404: {"description": "Product not found"}},
)
def delete_product(product_id: UUID):
    """
    Soft delete: deactivates the product instead of removing it.
    Existing orders keep a valid reference to the product.
    """
    index = _find_product_index(product_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    products_db[index] = products_db[index].model_copy(update={"is_active": False})
    logger.info("DELETE (soft) /api/v1/products/%s", product_id)

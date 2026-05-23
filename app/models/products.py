from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field
from enum import Enum


class Category(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    home = "home"
    sport = "sport"
    other = "other"


# Response model: full resource as stored and returned by the API.
# is_active enables soft delete — ordered products must never disappear.
class Product(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    # Decimal instead of float: avoids rounding errors (0.1 + 0.2 != 0.3).
    # FastAPI serializes Decimal to a JSON number via jsonable_encoder.
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
    category: Category
    is_active: bool = True


# POST body: no id (server-generated), is_active defaults to True.
class CreateProduct(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
    category: Category


# PATCH body: all fields optional — only sent fields are applied.
class UpdateProduct(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = Field(default=None, gt=0, decimal_places=2)
    stock: Optional[int] = Field(default=None, ge=0)
    category: Optional[Category] = None
    is_active: Optional[bool] = None


# PUT body: full replacement, no id (comes from URL only).
class ProductReplace(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
    category: Category
    is_active: bool = True

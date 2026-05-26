from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class Category(str, Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    FOOD = "food"
    HOME = "home"
    SPORT = "sport"
    OTHER = "other"


# Response model: full resource as stored and returned by the API.
# is_active enables soft delete — ordered products must never disappear.
class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None  # required — must be explicitly passed (even as None)
    # Decimal instead of float: avoids rounding errors (0.1 + 0.2 != 0.3).
    # FastAPI serializes Decimal to a JSON number via jsonable_encoder.
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
    category: Category
    is_active: bool = False  # products are inactive by default until explicitly activated


# POST body: no id (server-generated), is_active defaults to False.
class ProductCreate(BaseModel):
    name: str
    description: str | None  # required — must be explicitly passed (even as None)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
    category: Category


# PUT body: full replacement, no id (comes from URL only).
class ProductReplace(BaseModel):
    name: str
    description: str | None  # required — must be explicitly passed (even as None)
    price: Decimal = Field(gt=0, decimal_places=2)
    stock: int = Field(ge=0)
    category: Category
    is_active: bool


# PATCH body: all fields optional — only sent fields are applied.
class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category: Category | None = None
    is_active: bool | None = None

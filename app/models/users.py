from uuid import UUID
from pydantic import BaseModel, ConfigDict
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"


class Role(str, Enum):
    admin = "admin"
    customer = "customer"


# Response model: full resource as stored and returned by the API.
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    gender: Gender
    roles: list[Role]


# POST body: required fields, no id (server-generated).
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    roles: list[Role]


# PUT body: full replacement, no id (comes from URL only).
class UserReplace(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    roles: list[Role]


# PATCH body: all fields optional — only sent fields are applied.
class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender | None = None
    roles: list[Role] = []

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class Gender(str, Enum):
    male = "male"
    female = "female"


class Role(str, Enum):
    admin = "admin"
    customer = "customer"


# Response model: full resource as stored and returned by the API.
class User(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    gender: Gender
    roles: List[Role]


# POST body: required fields, no id (server-generated).
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    roles: List[Role]


# PATCH body: all fields optional — only sent fields are applied.
class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    roles: Optional[List[Role]] = None


# PUT body: full replacement, no id (comes from URL only).
class UserReplace(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    roles: List[Role]

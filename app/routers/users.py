from typing import List
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException

from app.models.users import (
    UserCreate,
    Gender,
    Role,
    UserUpdate,
    UserResponse,
    UserReplace,
)

import logging

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api/v1/users", tags=["User"])

# In-memory store — no database yet.
users_db: List[UserResponse] = [
    UserResponse(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        gender=Gender.male,
        roles=[Role.admin],
    ),
    UserResponse(
        id=uuid4(),
        first_name="Jane",
        last_name="Doe",
        gender=Gender.female,
        roles=[Role.customer],
    ),
    UserResponse(
        id=uuid4(),
        first_name="James",
        last_name="Gabriel",
        gender=Gender.male,
        roles=[Role.customer],
    ),
]


def _find_user_index(user_id: UUID) -> int | None:
    """Return the index in users_db, or None if not found."""
    for index, user in enumerate(users_db):
        if user.id == user_id:
            return index
    return None


# --- Collection ---


@router.get("", response_model=List[UserResponse])
def get_users():
    """List all users."""
    logger.info("GET /api/v1/users - %s user(s)", len(users_db))
    return users_db


@router.post("", response_model=UserResponse, status_code=201)
def create_user(payload: UserCreate):
    """Create a user. The id is always server-generated."""
    new_user = UserResponse(id=uuid4(), **payload.model_dump())
    users_db.append(new_user)
    logger.info("POST /api/v1/users - created id=%s", new_user.id)
    return new_user


# --- Single resource by id (UUID in URL, never list index) ---


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"description": "User not found"}},
)
def get_user(user_id: UUID):
    """Retrieve a user by their UUID."""
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return users_db[index]


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"description": "User not found"}},
)
def patch_user(user_id: UUID, payload: UserUpdate):
    """
    Partial update (PATCH).
    Only fields present in the JSON body are modified (exclude_unset).
    """
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Pydantic merge — no manual per-field if checks needed.
    users_db[index] = users_db[index].model_copy(
        update=payload.model_dump(exclude_unset=True),
    )
    logger.info("PATCH /api/v1/users/%s", user_id)
    return users_db[index]


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    responses={404: {"description": "User not found"}},
)
def replace_user(user_id: UUID, payload: UserReplace):
    """Full replacement (PUT). All body fields required; id comes from the URL only."""
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    users_db[index] = UserResponse(id=user_id, **payload.model_dump())
    logger.info("PUT /api/v1/users/%s", user_id)
    return users_db[index]


@router.delete(
    "/{user_id}",
    status_code=204,
    responses={404: {"description": "User not found"}},
)
def delete_user(user_id: UUID):
    """Delete a user. Returns 204 with no body on success."""
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    users_db.pop(index)
    logger.info("DELETE /api/v1/users/%s", user_id)

from typing import List
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models.users import (
    CreateUser,
    Gender,
    Role,
    UpdateUser,
    User,
    UserReplace,
)

import logging

# Réutilise la config d'uvicorn : format, niveau et handlers déjà en place.
# Évite de reconfigurer le root logger et de polluer les logs tiers.
logger = logging.getLogger("uvicorn.error")

app = FastAPI()

# "Base de données" en mémoire pour l'exemple minimal.
db: List[User] = [
    User(
        id=uuid4(),
        first_name="John",
        last_name="Doe",
        gender=Gender.male,
        roles=[Role.admin],
    ),
    User(
        id=uuid4(),
        first_name="Jane",
        last_name="Doe",
        gender=Gender.female,
        roles=[Role.customer],
    ),
    User(
        id=uuid4(),
        first_name="James",
        last_name="Gabriel",
        gender=Gender.male,
        roles=[Role.customer],
    ),
]

app.mount("/static", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="app/templates")


def _find_user_index(user_id: UUID) -> int | None:
    """Retourne l'index dans db, ou None si l'utilisateur n'existe pas."""
    for index, user in enumerate(db):
        if user.id == user_id:
            return index
    return None


@app.get("/")
def root():
    return {"Hello": "World"}


# --- Collection ---


@app.get("/api/v1/users", response_model=List[User], tags=["User"])
def get_users():
    """Liste tous les utilisateurs."""
    logger.info("GET /api/v1/users - %s utilisateur(s)", len(db))
    return db


@app.post("/api/v1/users", response_model=User, status_code=201, tags=["User"])
def create_user(payload: CreateUser):
    """
    Crée un utilisateur.
    L'id est toujours généré par le serveur (le client ne le fournit pas).
    """
    new_user = User(id=uuid4(), **payload.model_dump())
    db.append(new_user)
    logger.info("POST /api/v1/users - créé id=%s", new_user.id)
    return new_user


# --- Ressource par id (UUID dans l'URL, jamais l'index de la liste) ---


@app.get(
    "/api/v1/users/{user_id}",
    response_model=User,
    tags=["User"],
    responses={404: {"description": "User not found"}},
)
def get_user(user_id: UUID):
    """Récupère un utilisateur par son identifiant."""
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return db[index]


@app.patch(
    "/api/v1/users/{user_id}",
    response_model=User,
    tags=["User"],
    responses={404: {"description": "User not found"}},
)
def patch_user(user_id: UUID, payload: UpdateUser):
    """
    Mise à jour partielle (PATCH).
    Seuls les champs présents dans le JSON sont modifiés (exclude_unset).
    """
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Fusion Pydantic : pas de if manuel par champ.
    db[index] = db[index].model_copy(
        update=payload.model_dump(exclude_unset=True),
    )
    logger.info("PATCH /api/v1/users/%s", user_id)
    return db[index]


@app.put(
    "/api/v1/users/{user_id}",
    response_model=User,
    tags=["User"],
    responses={404: {"description": "User not found"}},
)
def replace_user(user_id: UUID, payload: UserReplace):
    """
    Remplacement complet (PUT).
    Tous les champs du corps sont requis ; l'id vient uniquement de l'URL.
    """
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    db[index] = User(id=user_id, **payload.model_dump())
    logger.info("PUT /api/v1/users/%s", user_id)
    return db[index]


@app.delete(
    "/api/v1/users/{user_id}",
    status_code=204,
    tags=["User"],
    responses={404: {"description": "User not found"}},
)
def delete_user(user_id: UUID):
    """Supprime un utilisateur. Réponse vide en 204 si succès."""
    index = _find_user_index(user_id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    db.pop(index)
    logger.info("DELETE /api/v1/users/%s", user_id)

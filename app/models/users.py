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


# Modèle de réponse : ressource complète telle que stockée et renvoyée par l'API.
class User(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    gender: Gender
    roles: List[Role]


# Corps de POST : champs requis, sans id (généré côté serveur).
class CreateUser(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    roles: List[Role]


# Corps de PATCH : tous les champs optionnels ; seuls ceux envoyés sont appliqués.
class UpdateUser(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    roles: Optional[List[Role]] = None


# Corps de PUT : même forme que CreateUser (remplacement complet, id uniquement dans l'URL).
class UserReplace(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    roles: List[Role]

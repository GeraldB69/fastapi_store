from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.models.users import Gender, Role, User
from app.routers.users import users_db
from main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_users_db():
    """Reset the in-memory store to a known state before each test."""
    users_db.clear()
    users_db.extend([
        User(id=uuid4(), first_name="John", last_name="Doe", gender=Gender.male, roles=[Role.admin]),
        User(id=uuid4(), first_name="Jane", last_name="Doe", gender=Gender.female, roles=[Role.customer]),
    ])
    yield
    users_db.clear()


class TestGetUsers:
    def test_returns_all_users(self):
        response = client.get("/api/v1/users")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_response_shape(self):
        data = client.get("/api/v1/users").json()

        assert all({"id", "first_name", "last_name", "gender", "roles"} <= u.keys() for u in data)


class TestGetUser:
    def test_returns_user_by_id(self):
        user_id = str(users_db[0].id)

        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_unknown_id_returns_404(self):
        response = client.get(f"/api/v1/users/{uuid4()}")

        assert response.status_code == 404


class TestCreateUser:
    def test_creates_user_and_returns_201(self):
        payload = {"first_name": "Alice", "last_name": "Smith", "gender": "female", "roles": ["customer"]}

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Alice"
        assert "id" in data  # server-generated

    def test_id_is_server_generated(self):
        payload = {"first_name": "Bob", "last_name": "Smith", "gender": "male", "roles": ["customer"]}

        response = client.post("/api/v1/users", json=payload)

        assert "id" in response.json()

    def test_invalid_gender_returns_422(self):
        payload = {"first_name": "X", "last_name": "Y", "gender": "alien", "roles": ["customer"]}

        response = client.post("/api/v1/users", json=payload)

        assert response.status_code == 422

    def test_missing_field_returns_422(self):
        response = client.post("/api/v1/users", json={"first_name": "X"})

        assert response.status_code == 422


class TestPatchUser:
    def test_updates_only_sent_fields(self):
        user_id = str(users_db[0].id)
        original_last_name = users_db[0].last_name

        response = client.patch(f"/api/v1/users/{user_id}", json={"first_name": "Updated"})

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == original_last_name  # unchanged

    def test_unknown_id_returns_404(self):
        response = client.patch(f"/api/v1/users/{uuid4()}", json={"first_name": "X"})

        assert response.status_code == 404


class TestReplaceUser:
    def test_replaces_all_fields(self):
        user_id = str(users_db[0].id)
        payload = {"first_name": "New", "last_name": "Name", "gender": "female", "roles": ["customer"]}

        response = client.put(f"/api/v1/users/{user_id}", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "New"
        assert data["id"] == user_id  # id unchanged

    def test_unknown_id_returns_404(self):
        payload = {"first_name": "X", "last_name": "Y", "gender": "male", "roles": ["customer"]}

        response = client.put(f"/api/v1/users/{uuid4()}", json=payload)

        assert response.status_code == 404


class TestDeleteUser:
    def test_returns_204(self):
        user_id = str(users_db[0].id)

        response = client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 204
        assert response.content == b""  # no body

    def test_user_no_longer_exists_after_delete(self):
        user_id = str(users_db[0].id)
        client.delete(f"/api/v1/users/{user_id}")

        response = client.get(f"/api/v1/users/{user_id}")

        assert response.status_code == 404

    def test_unknown_id_returns_404(self):
        response = client.delete(f"/api/v1/users/{uuid4()}")

        assert response.status_code == 404

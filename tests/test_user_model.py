from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models.users import Gender, Role, UserResponse


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def valid_user_kwargs(user_id: UUID) -> dict:
    return {
        "id": user_id,
        "first_name": "Jane",
        "last_name": "Doe",
        "gender": Gender.female,
        "roles": [Role.customer],
    }


class TestUser:
    def test_create_with_enums(self, valid_user_kwargs: dict) -> None:
        user = UserResponse(**valid_user_kwargs)

        assert user.id == valid_user_kwargs["id"]
        assert user.first_name == "Jane"
        assert user.last_name == "Doe"
        assert user.gender is Gender.female
        assert user.roles == [Role.customer]

    def test_create_coerces_string_enums(self, user_id: UUID) -> None:
        user = UserResponse(
            id=user_id,
            first_name="John",
            last_name="Doe",
            gender=Gender.male,
            roles=[Role.admin, Role.customer],
        )

        assert user.gender is Gender.male
        assert user.roles == [Role.admin, Role.customer]

    def test_model_dump_and_validate_roundtrip(self, valid_user_kwargs: dict) -> None:
        user = UserResponse(**valid_user_kwargs)
        restored = UserResponse.model_validate(user.model_dump())

        assert restored == user

    def test_model_dump_json_contains_expected_fields(self, valid_user_kwargs: dict) -> None:
        user = UserResponse(**valid_user_kwargs)
        data = user.model_dump(mode="json")

        assert data["id"] == str(valid_user_kwargs["id"])
        assert data["gender"] == "female"
        assert data["roles"] == ["customer"]

    def test_missing_required_field_raises(self, user_id: UUID) -> None:
        with pytest.raises(ValidationError) as exc_info:
            UserResponse(id=user_id, first_name="Jane")

        fields = {err["loc"][0] for err in exc_info.value.errors()}
        assert "last_name" in fields
        assert "gender" in fields
        assert "roles" in fields

    def test_invalid_gender_raises(self, user_id: UUID) -> None:
        with pytest.raises(ValidationError):
            UserResponse(
                id=user_id,
                first_name="Jane",
                last_name="Doe",
                gender="other",
                roles=[Role.customer],
            )

    def test_invalid_role_raises(self, user_id: UUID) -> None:
        with pytest.raises(ValidationError):
            UserResponse(
                id=user_id,
                first_name="Jane",
                last_name="Doe",
                gender=Gender.female,
                roles=["superuser"],
            )

    def test_invalid_uuid_raises(self) -> None:
        with pytest.raises(ValidationError):
            UserResponse(
                id="not-a-uuid",
                first_name="Jane",
                last_name="Doe",
                gender=Gender.female,
                roles=[Role.customer],
            )

    def test_empty_roles_list_is_valid(self, user_id: UUID) -> None:
        user = UserResponse(
            id=user_id,
            first_name="Jane",
            last_name="Doe",
            gender=Gender.female,
            roles=[],
        )

        assert user.roles == []

    def test_model_copy_updates_fields(self, valid_user_kwargs: dict) -> None:
        user = UserResponse(**valid_user_kwargs)
        updated = user.model_copy(update={"first_name": "Janet"})

        assert updated.first_name == "Janet"
        assert updated.last_name == user.last_name
        assert updated.id == user.id
        assert user.first_name == "Jane"

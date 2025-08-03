import pytest
from httpx import AsyncClient
from starlette import status

from app.api.authentication.utils import get_password_hash, verify_password
from app.domain.enums import UserRoles
from app.uow.unit_of_work import UnitOfWork
from tests.constants import Urls
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_create_user_invalid_email(test_client: AsyncClient) -> None:
    response = await test_client.post(
        url=Urls.Users.CREATE,
        json={
            "email": "invalid-email",
            "first_name": "Bob",
            "last_name": "Feta",
            "password": "password",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_user_no_first_last_name(test_client: AsyncClient) -> None:
    response = await test_client.post(
        url=Urls.Users.CREATE,
        json={"email": "test@example.com", "password": "password"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_create_user_email_busy(test_client: AsyncClient, test_uow: UnitOfWork) -> None:
    hashed_password = get_password_hash("123456")
    user = await UserFactory.create_(uow=test_uow, hashed_password=hashed_password)
    user_data = {
        "email": user.email,
        "first_name": "Bob",
        "last_name": "Feta",
        "password": "123456",
    }
    response = await test_client.post(url=Urls.Users.CREATE, json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    response_json = response.json()
    assert response_json.get("detail") == "User with such email already exists."


@pytest.mark.parametrize(
    "role",
    UserRoles,
)
@pytest.mark.anyio
async def test_create_user_success(
    role,
    test_client: AsyncClient,
    test_uow: UnitOfWork,
) -> None:
    user_data = {
        "email": "bob.feta@example.com",
        "first_name": "Bob",
        "last_name": "Feta",
        "password": "password",
        "role": role.value,
    }
    response = await test_client.post(url=Urls.Users.CREATE, json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    for key, value in user_data.items():
        if key == "password":  # Skip password check as it is hashed and not returned
            continue
        assert response_json.get(key) == value, (
            f"Expected {key} to be {value}, got {response_json.get(key)}"
        )

    # Verify that the user was created in the database
    db_user = await test_uow.user.get_by_email(email=user_data["email"])
    assert db_user is not None, "User should be created in the database"
    assert db_user.email == user_data["email"]
    assert db_user.first_name == user_data["first_name"]
    assert db_user.last_name == user_data["last_name"]
    assert verify_password(user_data["password"], db_user.hashed_password)
    assert db_user.role == role, f"Expected role to be {role}, got {db_user.role}"

import pytest
from httpx import AsyncClient
from starlette import status

from app.api.authentication.dependencies import get_password_hash
from tests.conftest import TestSettings
from tests.constants import Urls
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_sign_up_invalid_email(
    test_settings: TestSettings, unauthenticated_client: AsyncClient
) -> None:
    response = await unauthenticated_client.post(
        url=Urls.Auth.SIGN_UP,
        json={
            "email": "invalid-email",
            "first_name": "Bob",
            "last_name": "Feta",
            "password": "password",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_sign_up_no_first_last_name(
    test_settings: TestSettings, unauthenticated_client: AsyncClient
) -> None:
    response = await unauthenticated_client.post(
        url=Urls.Auth.SIGN_UP,
        json={"email": "test@example.com", "password": "password"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.anyio
async def test_sign_up_email_busy(
    test_settings: TestSettings, unauthenticated_client: AsyncClient
) -> None:
    hashed_password = get_password_hash("123456")
    user = await UserFactory.create_(hashed_password=hashed_password)
    user_data = {
        "email": user.email,
        "first_name": "Bob",
        "last_name": "Feta",
        "password": "123456",
    }
    response = await unauthenticated_client.post(
        url=Urls.Auth.SIGN_UP,
        json=user_data,
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    response_json = response.json()
    assert response_json.get("detail") == "User with such email already exists."


@pytest.mark.anyio
async def test_sign_up_success(
    test_settings: TestSettings, unauthenticated_client: AsyncClient
) -> None:
    user_data = {
        "email": "bob.feta@example.com",
        "first_name": "Bob",
        "last_name": "Feta",
        "password": "password",
    }
    response = await unauthenticated_client.post(
        url=Urls.Auth.SIGN_UP,
        json=user_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert "access_token" in response_json
    for key, value in user_data.items():
        if key == "password":  # Skip password check as it is hashed and not returned
            continue
        assert response_json.get(key) == value, (
            f"Expected {key} to be {value}, got {response_json.get(key)}"
        )

import pytest
from httpx import AsyncClient
from starlette import status

from app.api.authentication.utils import get_password_hash
from app.uow.unit_of_work import UnitOfWork
from tests.constants import Urls
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_login_invalid_credentials(unauthenticated_client: AsyncClient) -> None:
    response = await unauthenticated_client.post(
        url=Urls.Auth.LOGIN,
        json={
            "email": "invalid@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert response_json.get("detail") == "Unable to find user with provided email."


@pytest.mark.anyio
async def test_login_success(unauthenticated_client: AsyncClient, test_uow: UnitOfWork) -> None:
    hashed_password = get_password_hash("123456")
    user = await UserFactory.create_(uow=test_uow, hashed_password=hashed_password)
    # 1. Send invalid credentials
    user_data = {"email": user.email, "password": "wrongpassword"}
    response = await unauthenticated_client.post(url=Urls.Auth.LOGIN, json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    response_json = response.json()
    assert response_json.get("detail") == "Unable to login with provided credentials."

    # 2. Send valid credentials
    user_data = {"email": user.email, "password": "123456"}
    response = await unauthenticated_client.post(url=Urls.Auth.LOGIN, json=user_data)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert "access_token" in response_json
    for key, value in user_data.items():
        if key == "password":  # Skip password check as it is hashed and not returned
            continue
        assert response_json.get(key) == value, (
            f"Expected {key} to be {value}, got {response_json.get(key)}"
        )

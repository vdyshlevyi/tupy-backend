import pytest
from httpx import AsyncClient
from starlette import status

from tests.conftest import TestSettings
from tests.constants import Urls


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

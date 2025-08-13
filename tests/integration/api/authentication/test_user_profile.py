import pytest
from httpx import AsyncClient
from starlette import status

from app.api.authentication.utils import generate_access_token
from app.uow.unit_of_work import UnitOfWork
from tests.conftest import TestSettings
from tests.constants import Urls
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_get_user_profile(
    unauthenticated_client: AsyncClient,
    test_uow: UnitOfWork,
    test_settings: TestSettings,
) -> None:
    user = await UserFactory.create_(uow=test_uow)
    access_token = generate_access_token(
        user,
        exp_minutes=test_settings.ACCESS_TOKEN_EXP_MINUTES,
        secret_key=test_settings.SECRET_KEY,
        algorithm=test_settings.ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await unauthenticated_client.get(url=Urls.Auth.PROFILE, headers=headers)
    assert response.status_code == status.HTTP_200_OK, response.text

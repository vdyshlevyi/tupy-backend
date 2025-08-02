import pytest
from httpx import AsyncClient
from starlette import status

from app.uow.unit_of_work import UnitOfWork
from tests.constants import Urls
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_get_users_success(
    test_client: AsyncClient,
    test_uow: UnitOfWork,
) -> None:
    await UserFactory.create_(uow=test_uow)
    await UserFactory.create_(uow=test_uow)

    response = await test_client.get(url=Urls.Users.GET_ALL)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    items = response_json.get("items", [])
    assert len(items) == 3  # 2 users created by UserFactory + 1 admin user created for test_client

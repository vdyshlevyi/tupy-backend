import pytest
from httpx import AsyncClient
from starlette import status

from app.domain.users import User
from app.uow.unit_of_work import UnitOfWork
from tests.constants import Urls
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_get_user_by_id(test_client: AsyncClient, test_uow: UnitOfWork) -> None:
    user = await UserFactory.create_(uow=test_uow)
    response = await test_client.get(url=Urls.Users.GET_BY_ID.format(user_id=user.id))
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert response_json.get("id") == user.id
    assert response_json.get("email") == user.email
    assert response_json.get("first_name") == user.first_name
    assert response_json.get("last_name") == user.last_name
    assert response_json.get("role") == user.role.value
    assert response_json.get("hashed_password") is None  # Ensure password is not returned

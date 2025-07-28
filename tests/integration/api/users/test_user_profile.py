import pytest
from httpx import AsyncClient
from starlette import status

from tests.constants import Urls


@pytest.mark.anyio
async def test_get_user_profile(test_client: AsyncClient) -> None:
    response = await test_client.get(url=Urls.Users.PROFILE)
    assert response.status_code == status.HTTP_200_OK

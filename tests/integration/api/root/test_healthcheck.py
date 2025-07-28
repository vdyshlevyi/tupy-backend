import pytest
from httpx import AsyncClient
from starlette import status

from tests.constants import Urls


@pytest.mark.anyio
async def test_health_check(unauthenticated_client: AsyncClient) -> None:
    response = await unauthenticated_client.get(url=Urls.HEALTHCHECK)
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"result": "success"}

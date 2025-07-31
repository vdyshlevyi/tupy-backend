import pytest
from httpx import AsyncClient
from starlette import status

from tests.conftest import TestSettings
from tests.constants import Urls


@pytest.mark.anyio
async def test_info(test_client: AsyncClient, test_settings: TestSettings) -> None:
    response = await test_client.get(url=Urls.Common.INFO)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"title": test_settings.TITLE, "version": test_settings.VERSION}

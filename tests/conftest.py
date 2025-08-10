from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pytest
from pydantic import computed_field
from pydantic_settings import SettingsConfigDict

from app.config import Settings


class TestSettings(Settings):
    """Settings for tests."""

    TITLE: str = "Test Title"
    SECRET_KEY: str = "1234567890"

    DATABASE_URI: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_tupy_backend"

    USE_TESTCONTAINERS: bool = True
    POSTGRES_TEMPLATE_DB: str = "template_test_tupy_backend"
    POSTGRES_DB: str = "test_tupy_backend"
    POSTGRES_PORT_EXTERNAL: int | None = None
    POSTGRES_DOCKER_IMAGE: str = "postgis/postgis:16-3.4"

    model_config = SettingsConfigDict(env_file=Path(__file__).parent / ".testenv")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def get_template_postgres_uri(self) -> str:
        """Build database URI for DB template."""
        parsed = urlparse(self.DATABASE_URI)
        netloc = f"{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"
        path = f"/{self.POSTGRES_TEMPLATE_DB}"
        return urlunparse((parsed.scheme, netloc, path, "", "", ""))


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=False)
def test_settings() -> TestSettings:
    """Settings for tests."""
    return TestSettings()

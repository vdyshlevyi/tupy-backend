import os
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pytest
from alembic import command
from alembic.config import Config
from dependency_injector.wiring import Provide, inject
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)
from testcontainers.core.generic import DbContainer  # type: ignore[import-untyped]
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from app.api.authentication.dependencies import generate_access_token, get_password_hash
from app.containers import Container
from app.domain import MinimalBase
from app.main import make_app
from app.types import FastAPIWithContainer
from tests.conftest import TestSettings
from tests.factories import UserFactory

DROP_TABLE_SQL = """DROP TABLE IF EXISTS {name} CASCADE;"""
SET_IS_TEMPLATE_SQL = """ALTER DATABASE {name} WITH is_template = true;"""
DROP_DATABASE_SQL = """DROP DATABASE IF EXISTS {name};"""
COPY_DATABASE_SQL = """CREATE DATABASE {name} TEMPLATE {template};"""


@pytest.fixture(scope="session", autouse=True)
@inject
def _database_container_instance(
    settings: TestSettings = Provide[Container.settings],
) -> DbContainer | None:
    """Create a PostgreSQL container for tests."""
    # Split database URI into components
    parsed = urlparse(settings.DATABASE_URI)
    # Create a PostgresSQL instance in Docker container
    container = PostgresContainer(
        image=settings.POSTGRES_DOCKER_IMAGE,
        dbname=settings.POSTGRES_TEMPLATE_DB,
        username=parsed.username,
        password=parsed.password,
    )
    if settings.POSTGRES_PORT_EXTERNAL:
        container = container.with_bind_ports(5432, settings.POSTGRES_PORT_EXTERNAL)
    # Start the container with PostgreSQL
    container_instance = container.start()
    # Save a new connection URL
    hostname = container_instance.get_container_host_ip()
    port = int(container_instance.get_exposed_port(5432))
    netloc = f"{parsed.username}:{parsed.password}@{hostname}:{port}"
    path = f"/{settings.POSTGRES_DB}"

    settings.DATABASE_URI = urlunparse((parsed.scheme, netloc, path, "", "", ""))

    return container_instance


@pytest.fixture(scope="session", autouse=False)
@inject
async def _setup_database(
    _database_container_instance,
    settings: TestSettings = Provide[Container.settings],
) -> None:
    """Clean up the database before test session."""
    engine = create_async_engine(url=settings.get_template_postgres_uri, echo=False)
    async with engine.begin() as conn:
        # Mark database as template
        await conn.execute(text(SET_IS_TEMPLATE_SQL.format(name=settings.POSTGRES_TEMPLATE_DB)))
        # Drop Alembic migrations table if it exists
        await conn.execute(text(DROP_TABLE_SQL.format(name="alembic_version")))
        # Drop all tables from MinimalBase metadata
        await conn.run_sync(MinimalBase.metadata.drop_all)

    await engine.dispose()


def apply_migrations(db_uri) -> None:
    """Apply Alembic migrations for the empty database."""
    alembic_directory = Path(__file__).parent.parent.parent

    # Save current working directory
    original_dir = Path.cwd()

    try:
        # Change to the alembic directory temporarily
        os.chdir(alembic_directory)
        alembic_cfg = Config(f"{alembic_directory}/alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_uri)
        # Apply the migrations
        command.upgrade(config=alembic_cfg, revision="head")
    finally:
        # Restore the original working directory
        os.chdir(original_dir)


@pytest.fixture(scope="session", autouse=False)
@inject
def _migrate_database(
    _setup_database, settings: TestSettings = Provide[Container.settings]
) -> None:
    """Apply migrations to the test database."""
    apply_migrations(db_uri=settings.get_template_postgres_uri)


@pytest.fixture(scope="function", autouse=False)
@inject
async def _copy_database(
    _migrate_database,
    settings: TestSettings = Provide[Container.settings],
) -> None:
    """Copy database from template."""
    engine = create_async_engine(url=settings.get_template_postgres_uri, echo=False)

    async with engine.connect() as conn:
        # Enable autocommit mode for DROP DATABASE
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        # Drop database if exists
        await conn.execute(text(DROP_DATABASE_SQL.format(name=settings.POSTGRES_DB)))
        # Create new database from template
        raw_sql = COPY_DATABASE_SQL.format(
            name=settings.POSTGRES_DB,
            template=settings.POSTGRES_TEMPLATE_DB,
        )
        await conn.execute(text(raw_sql))
    await engine.dispose()


@pytest.fixture(scope="session", autouse=False)
def test_app(setup_container) -> FastAPIWithContainer:
    """Create test FastAPI application."""
    app = make_app()
    app.container = setup_container
    return app


@pytest.fixture(scope="function", autouse=False)
def unauthenticated_client(
    _copy_database,
    test_app: FastAPIWithContainer,
) -> AsyncClient:
    """Build database and create unauthenticated test client."""
    return AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test")


@pytest.fixture(scope="function", autouse=False)
@inject
async def test_client(
    _copy_database,
    test_app: FastAPIWithContainer,
) -> AsyncClient:
    """Build database and create authenticated test client."""
    hashed_password = get_password_hash("123456")
    user = await UserFactory.create_(hashed_password=hashed_password)
    access_token = generate_access_token(user)
    headers = {"Authorization": f"Bearer {access_token}"}
    return AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        headers=headers,
    )

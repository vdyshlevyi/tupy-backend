import os
from collections.abc import AsyncGenerator
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)
from testcontainers.core.generic import DbContainer  # type: ignore[import-untyped]
from testcontainers.postgres import PostgresContainer  # type: ignore[import-untyped]

from app.api.authentication.utils import generate_access_token, get_password_hash
from app.db.database import DatabaseSessionManager
from app.dependencies.db import get_unit_of_work
from app.dependencies.settings import get_settings
from app.domain import MinimalBase
from app.main import fastapi_app
from app.uow.unit_of_work import UnitOfWork
from tests.conftest import TestSettings
from tests.factories import UserFactory

DROP_TABLE_SQL = """DROP TABLE IF EXISTS {name} CASCADE;"""
SET_IS_TEMPLATE_SQL = """ALTER DATABASE {name} WITH is_template = true;"""
DROP_DATABASE_SQL = """DROP DATABASE IF EXISTS {name};"""
COPY_DATABASE_SQL = """CREATE DATABASE {name} TEMPLATE {template};"""


####################################################################################################
# Session fixtures
####################################################################################################
@pytest.fixture(scope="session", autouse=True)
def _database_container_instance(test_settings: TestSettings) -> DbContainer | None:
    """Create a PostgreSQL container for tests."""
    # Split database URI into components
    parsed = urlparse(test_settings.DATABASE_URI)
    # Create a PostgresSQL instance in Docker container
    container = PostgresContainer(
        image=test_settings.POSTGRES_DOCKER_IMAGE,
        dbname=test_settings.POSTGRES_TEMPLATE_DB,
        username=parsed.username,
        password=parsed.password,
    )
    if test_settings.POSTGRES_PORT_EXTERNAL:
        container = container.with_bind_ports(5432, test_settings.POSTGRES_PORT_EXTERNAL)
    # Start the container with PostgreSQL
    container_instance = container.start()
    # Save a new connection URL
    hostname = container_instance.get_container_host_ip()
    port = int(container_instance.get_exposed_port(5432))
    netloc = f"{parsed.username}:{parsed.password}@{hostname}:{port}"
    path = f"/{test_settings.POSTGRES_DB}"

    test_settings.DATABASE_URI = urlunparse((parsed.scheme, netloc, path, "", "", ""))

    return container_instance


@pytest.fixture(scope="session", autouse=False)
async def _setup_database(
    _database_container_instance,
    test_settings: TestSettings,
) -> None:
    """Clean up the database before test session."""
    engine = create_async_engine(url=test_settings.get_template_postgres_uri, echo=False)
    async with engine.begin() as conn:
        # Mark database as template
        await conn.execute(
            text(SET_IS_TEMPLATE_SQL.format(name=test_settings.POSTGRES_TEMPLATE_DB))
        )
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
def _migrate_database(_setup_database, test_settings: TestSettings) -> None:
    """Apply migrations to the test database."""
    apply_migrations(db_uri=test_settings.get_template_postgres_uri)


@pytest.fixture(scope="session", autouse=False)
async def test_app(_migrate_database, test_settings: TestSettings) -> FastAPI:
    """Create test FastAPI application."""

    async def override_get_settings() -> TestSettings:
        """Override settings for testing."""
        return test_settings

    async def override_get_unit_of_work() -> AsyncGenerator:
        db_session_manager = fastapi_app.extra["db_session_manager"]
        db = db_session_manager.get_db()
        async with UnitOfWork(db) as uow:
            yield uow

    fastapi_app.dependency_overrides[get_settings] = override_get_settings
    fastapi_app.dependency_overrides[get_unit_of_work] = override_get_unit_of_work

    return fastapi_app


####################################################################################################
# Function fixtures
####################################################################################################
@pytest.fixture(scope="function", autouse=False)
async def _copy_database(test_app, test_settings: TestSettings) -> None:
    """Copy database from template."""
    db_session_manager = test_app.extra.get("db_session_manager")
    if db_session_manager:
        await db_session_manager.dispose()
    engine = create_async_engine(url=test_settings.get_template_postgres_uri, echo=False)

    async with engine.connect() as conn:
        # Enable autocommit mode for DROP DATABASE
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        # Drop database if exists
        await conn.execute(text(DROP_DATABASE_SQL.format(name=test_settings.POSTGRES_DB)))
        # Create new database from template
        raw_sql = COPY_DATABASE_SQL.format(
            name=test_settings.POSTGRES_DB,
            template=test_settings.POSTGRES_TEMPLATE_DB,
        )
        await conn.execute(text(raw_sql))
    await engine.dispose()

    test_app.extra["db_session_manager"] = DatabaseSessionManager(test_settings.DATABASE_URI)


@pytest.fixture(scope="function", autouse=False)
async def test_uow(_copy_database, test_app: FastAPI) -> AsyncGenerator:
    """Test UnitOfWork using shared db_session_manager from app."""
    db_session_manager = test_app.extra["db_session_manager"]
    db = db_session_manager.get_db()
    async with UnitOfWork(db) as uow:
        yield uow


@pytest.fixture(scope="function", autouse=False)
async def unauthenticated_client(
    test_app: FastAPI,
    test_uow: UnitOfWork,
) -> AsyncClient:
    """Build database and create unauthenticated test client."""
    return AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test")


@pytest.fixture(scope="function", autouse=False)
async def test_client(test_app: FastAPI, test_uow: UnitOfWork) -> AsyncClient:
    """Build database and create authenticated test client."""
    hashed_password = get_password_hash("123456")
    user = await UserFactory.create_(uow=test_uow, hashed_password=hashed_password)
    access_token = generate_access_token(user)
    headers = {"Authorization": f"Bearer {access_token}"}
    return AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
        headers=headers,
    )

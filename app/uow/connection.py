from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool


class AsyncSQLAlchemy:
    def __init__(self, db_uri: str) -> None:
        self._db_uri = db_uri
        self._engine: AsyncEngine = create_async_engine(
            self._db_uri,
            echo=False,  # Set to True to see SQL queries
            poolclass=NullPool,
        )
        self._session_factory = self.init_session_factory()

    async def connect(self, **kwargs) -> None:
        self._engine = create_async_engine(self._db_uri, **kwargs)
        async with self._engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def disconnect(self) -> None:
        await self._engine.dispose()

    def init_session_factory(self, autocommit: bool = False, autoflush: bool = False):
        return async_scoped_session(
            sessionmaker(
                autocommit=autocommit,
                autoflush=autoflush,
                bind=self._engine,  # type: ignore[call-overload]
                class_=AsyncSession,
            ),
            scopefunc=current_task,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_scoped_session:
        return self._session_factory

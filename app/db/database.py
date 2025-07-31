import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


class AsyncSQLAlchemy:
    def __init__(self, session_factory: async_sessionmaker, engine: AsyncEngine) -> None:
        self.session_factory = session_factory
        self.engine = engine


class DatabaseSessionManager:
    def __init__(self, url: str) -> None:
        self._url = url
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            bind=self._engine, autoflush=False, autocommit=False
        )

    def get_db(self) -> AsyncSQLAlchemy:
        return AsyncSQLAlchemy(session_factory=self._session_maker, engine=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def dispose(self):
        await self._engine.dispose()

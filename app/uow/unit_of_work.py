from typing import TYPE_CHECKING, Any

from sqlalchemy import Executable, Result

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from app.domain import User
from app.uow.connection import AsyncSQLAlchemy
from app.uow.user.repository import UserRepository


class UnitOfWork:
    def __init__(self, db: AsyncSQLAlchemy) -> None:
        self.session_factory = db.session_factory
        self.engine = db.engine

    async def __aenter__(self) -> "UnitOfWork":
        """Start unit of work here"""
        self.session: AsyncSession = self.session_factory()

        self.user = UserRepository(session=self.session, model=User)

        return self

    async def __aexit__(self, *args) -> None:
        """Close unit of work here"""
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def execute(self, query: Executable) -> Result[Any]:
        return await self.session.execute(query)

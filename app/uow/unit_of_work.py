from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import Executable, Result

from app.db.database import AsyncSQLAlchemy
from app.domain import Order, User
from app.uow.order.repository import OrderRepository
from app.uow.user.repository import UserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class UnitOfWork:
    def __init__(self, db: AsyncSQLAlchemy) -> None:
        self.session_factory = db.session_factory
        self.engine = db.engine

    async def __aenter__(self) -> "UnitOfWork":
        """Start unit of work here"""
        self._session: AsyncSession = self.session_factory()

        self.order = OrderRepository(session=self._session, model=Order)
        self.user = UserRepository(session=self._session, model=User)

        return self

    async def __aexit__(self, *args) -> None:
        """Close unit of work here"""
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def refresh(self, instance: T) -> None:
        await self._session.refresh(instance)

    def add(self, instance: T) -> None:
        self._session.add(instance)

    async def execute(self, query: Executable) -> Result[Any]:
        return await self._session.execute(query)

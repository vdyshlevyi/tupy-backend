from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db.database import AsyncSQLAlchemy
from app.db.session import db_session_manager
from app.uow.unit_of_work import UnitOfWork


async def get_unit_of_work() -> AsyncGenerator:
    db: AsyncSQLAlchemy = db_session_manager.get_db()
    async with UnitOfWork(db) as uow:
        yield uow

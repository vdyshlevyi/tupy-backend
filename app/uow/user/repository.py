from sqlalchemy import select

from app.domain import User
from app.uow.repository import BaseModelRepository


class UserRepository(BaseModelRepository):
    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).filter(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).filter(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, flush: bool = False, **data):
        """Create a new record in DB."""
        record = self.model(**data)
        self.session.add(record)
        if flush:
            await self.session.flush([record])
        return record

from collections.abc import Sequence

from sqlalchemy import func, select

from app.domain import User
from app.uow.repository import BaseModelRepository


class UserRepository(BaseModelRepository):
    async def get_all(self) -> Sequence[User]:
        query = select(User)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_paginated_all(self, page: int, page_size: int) -> tuple[Sequence[User], int]:
        """Get paginated list of users."""
        # Fetch users with pagination parameters
        offset = (page - 1) * page_size
        query = select(User).offset(offset).limit(page_size)
        result = await self._session.execute(query)
        users = result.scalars().all()

        # Count total number of users
        count_query = select(func.count()).select_from(User)
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        return users, total

    async def get_by_id(self, user_id: int) -> User | None:
        query = select(User).filter(User.id == user_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).filter(User.email == email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, flush: bool = False, **data):
        """Create a new record in DB."""
        record = self._model(**data)
        self._session.add(record)
        if flush:
            await self._session.flush([record])
        return record

from collections.abc import Sequence

from sqlalchemy import func, select

from app.domain import Order
from app.uow.repository import BaseModelRepository


class OrderRepository(BaseModelRepository):
    async def get_all(self) -> Sequence[Order]:
        query = select(Order)
        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_paginated_all(self, page: int, page_size: int) -> tuple[Sequence[Order], int]:
        """Get paginated list of orders."""
        # Fetch orders with pagination parameters
        offset = (page - 1) * page_size
        query = select(Order).offset(offset).limit(page_size)
        result = await self._session.execute(query)
        orders = result.scalars().all()

        # Count total number of orders
        count_query = select(func.count()).select_from(Order)
        total_result = await self._session.execute(count_query)
        total = total_result.scalar_one()

        return orders, total

    async def get_by_id(self, id_: int) -> Order | None:
        query = select(Order).filter(Order.id == id_)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, flush: bool = False, **data):
        """Create a new order record in DB."""
        record = self._model(**data)
        self._session.add(record)
        if flush:
            await self._session.flush([record])
        return record

    async def get_orders_by_distance_range(
        self, min_distance_km: float | None = None, max_distance_km: float | None = None
    ) -> Sequence[Order]:
        """Get orders filtered by distance range."""
        query = select(Order)

        if min_distance_km is not None:
            query = query.filter(Order.distance_km >= min_distance_km)
        if max_distance_km is not None:
            query = query.filter(Order.distance_km <= max_distance_km)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def get_orders_by_duration_range(
        self,
        min_duration_minutes: float | None = None,
        max_duration_minutes: float | None = None,
    ) -> Sequence[Order]:
        """Get orders filtered by duration range."""
        query = select(Order)

        if min_duration_minutes is not None:
            query = query.filter(Order.duration_minutes >= min_duration_minutes)
        if max_duration_minutes is not None:
            query = query.filter(Order.duration_minutes <= max_duration_minutes)

        result = await self._session.execute(query)
        return result.scalars().all()

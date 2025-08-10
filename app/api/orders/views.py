from logging import getLogger

from fastapi import APIRouter, Depends, Query
from starlette import status

from app.api.orders.schemas import AddOrderSchema, OrdersSchema, ViewOrderSchema
from app.dependencies.db import get_unit_of_work
from app.domain import Order
from app.uow.unit_of_work import UnitOfWork

logger = getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "",
    response_model=ViewOrderSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order.",
)
async def create_order(
    body: AddOrderSchema,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> Order:
    """Create a new order."""
    # Create order data
    order_data = {
        "name": body.name,
        "description": body.description,
        # Convert lat/lng points to WKT format for PostGIS
        "start_point": body.start_point.to_wkt(),
        # Convert lat/lng points to WKT format for PostGIS
        "end_point": body.end_point.to_wkt(),
        "distance_km": body.distance_km,
        "duration_minutes": body.duration_minutes,
    }

    db_order = await uow.order.create(**order_data, flush=True)
    await uow.commit()
    await uow.refresh(db_order)

    return db_order


@router.get(
    "",
    response_model=OrdersSchema,
    summary="Get all orders.",
    status_code=status.HTTP_200_OK,
)
async def get_all_orders(
    uow: UnitOfWork = Depends(get_unit_of_work),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=2, le=100),
) -> dict:
    """Get all orders."""
    orders, total = await uow.order.get_paginated_all(page=page, page_size=page_size)
    return {"items": orders, "total": total, "page": page, "page_size": page_size}

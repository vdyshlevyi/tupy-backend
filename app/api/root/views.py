from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.root.schemas import HealthCheckSchema
from app.containers import Container
from app.uow.connection import AsyncSQLAlchemy

router = APIRouter(tags=["infrastructure"])


@router.get(
    path="/healthcheck",
    response_model=HealthCheckSchema,
    status_code=status.HTTP_200_OK,
    tags=["infrastructure"],
)
@inject
async def healthcheck(db: AsyncSQLAlchemy = Depends(Provide[Container.db])) -> dict:
    async with AsyncSession(db._engine) as session:
        await session.execute(text("SELECT 1"))

    return {"result": "success"}

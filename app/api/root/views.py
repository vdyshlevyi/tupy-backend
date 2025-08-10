from fastapi import APIRouter
from fastapi.params import Depends
from sqlalchemy import text
from starlette import status

from app.api.root.schemas import HealthCheckSchema
from app.dependencies.db import get_unit_of_work
from app.uow.unit_of_work import UnitOfWork

router = APIRouter(tags=["infrastructure"])


@router.get(
    path="/healthcheck",
    response_model=HealthCheckSchema,
    status_code=status.HTTP_200_OK,
    tags=["infrastructure"],
)
async def healthcheck(uow: UnitOfWork = Depends(get_unit_of_work)) -> dict:  # type: ignore[assignment]
    await uow.execute(text("SELECT 1"))
    return {"result": "success"}

from fastapi import APIRouter
from starlette import status

from app.api.root.schemas import HealthCheckSchema

router = APIRouter(tags=["infrastructure"])


@router.get(
    path="/healthcheck",
    response_model=HealthCheckSchema,
    status_code=status.HTTP_200_OK,
    tags=["infrastructure"],
)
async def healthcheck() -> dict:
    # async with AsyncSession(db._engine) as session:
    #     await session.execute(text("SELECT 1"))

    return {"result": "success"}

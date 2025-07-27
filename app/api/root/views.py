from fastapi import APIRouter
from starlette import status

from app.api.root.schemas import HealthCheckSchema

router = APIRouter(tags=["infrastructure"])


@router.get(
    path="/healthcheck",
    summary="Health check",
    response_model=HealthCheckSchema,
    status_code=status.HTTP_200_OK,
)
async def healthcheck() -> dict:
    """Healthcheck endpoint for infrastructure monitoring."""
    return {"message": "Welcome to FastAPI!!!"}

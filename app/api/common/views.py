from logging import getLogger

from fastapi import APIRouter, Depends
from starlette import status

from app.api.common.schemas import InfoSchema
from app.config import Settings, get_settings

logger = getLogger(__name__)

router = APIRouter(tags=["common"], prefix="/common", dependencies=[])


@router.get(
    path="/info",
    summary="General info",
    response_model=InfoSchema,
    status_code=status.HTTP_200_OK,
)
async def info(settings: Settings = Depends(get_settings)) -> dict:
    """General info about app."""
    return {"title": settings.TITLE, "version": settings.VERSION}

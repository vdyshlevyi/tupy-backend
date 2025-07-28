from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status

from app.api.authentication.dependencies import get_request_user
from app.api.common.schemas import InfoSchema
from app.config import Settings
from app.containers import Container

logger = getLogger(__name__)

router = APIRouter(tags=["common"], prefix="/common", dependencies=[Depends(get_request_user)])


@router.get(
    path="/info",
    summary="General info",
    response_model=InfoSchema,
    status_code=status.HTTP_200_OK,
)
@inject
async def info(
    settings: Settings = Depends(Provide[Container.settings]),
) -> dict:
    """General info about app."""
    return {"title": settings.TITLE, "version": settings.VERSION}

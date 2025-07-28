from logging import getLogger

from fastapi import APIRouter, Depends
from starlette import status

from app.api.authentication.dependencies import get_request_user
from app.api.users.schemas import ViewProfileSchema
from app.domain import User

logger = getLogger(__name__)

router = APIRouter(prefix="/users", dependencies=[Depends(get_request_user)])


@router.get(
    "/profile",
    response_model=ViewProfileSchema,
    summary="View user's profile.",
    status_code=status.HTTP_200_OK,
    tags=["profile"],
)
async def view_profile(request_user: User = Depends(get_request_user)) -> User:
    """View user's profile."""
    logger.info(f"request_user is: {request_user}")
    # go to Redis and get cached user data
    return request_user

from logging import getLogger

from fastapi import APIRouter, Depends
from starlette import status

from app.api.authentication.schemas import (
    LoginSchema,
    LoginSuccessSchema,
    ViewProfileSchema,
)
from app.api.authentication.utils import (
    generate_access_token,
    get_request_user,
    verify_password,
)
from app.api.exceptions import APIValidationError
from app.config import Settings
from app.dependencies.db import get_unit_of_work
from app.dependencies.settings import get_settings
from app.domain.users import User
from app.uow.unit_of_work import UnitOfWork

logger = getLogger(__name__)

router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post(
    "/login",
    response_model=LoginSuccessSchema,
    status_code=status.HTTP_200_OK,
    summary="Login an existing user.",
)
async def login(
    body: LoginSchema,
    settings: Settings = Depends(get_settings),
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> User:
    """Login an existing user."""
    error = "Unable to login with provided credentials."
    login_exc = APIValidationError(error)

    db_user = await uow.user.get_by_email(email=body.email)
    if not db_user:
        raise login_exc
    if db_user and verify_password(
        plain_password=body.password,
        hashed_password=db_user.hashed_password,
    ):
        access_token = generate_access_token(
            user=db_user,
            exp_minutes=settings.ACCESS_TOKEN_EXP_MINUTES,
            secret_key=settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        db_user.access_token = access_token  # type: ignore[attr-defined]
        return db_user
    raise login_exc


@router.get(
    "/profile",
    response_model=ViewProfileSchema,
    status_code=status.HTTP_200_OK,
    summary="View user's profile.",
)
async def view_profile(request_user: User = Depends(get_request_user)) -> User:
    """View user's profile."""
    logger.info(f"request_user is: {request_user}")
    return request_user

from logging import getLogger

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette import status

from app.api.authentication.dependencies import (
    generate_access_token,
    get_request_user,
    verify_password,
)
from app.api.authentication.schemas import (
    InfoSchema,
    LoginSchema,
    LoginSuccessSchema,
    SignUpSchema,
    ViewProfileSchema,
)
from app.api.exceptions import APIValidationError, ConflictError
from app.containers import Container
from app.domain.users import User
from app.uow.unit_of_work import UnitOfWork

logger = getLogger(__name__)

router = APIRouter(prefix="/authentication")


# TODO(Valerii Dyshlevyi): Use rate limits here
@router.post(
    "/sign-up",
    response_model=InfoSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Sign up for new users.",
    tags=["authentication"],
)
@inject
async def sign_up(
    body: SignUpSchema,
    unit_of_work: UnitOfWork = Depends(Provide[Container.unit_of_work]),
) -> dict:
    """Sign up for new users."""
    async with unit_of_work as uow:
        db_user = await uow.user.get_by_email(email=body.email)
        if db_user:
            error = "User with such email already exists."
            raise ConflictError(error)

        db_user = await uow.user.create(body=body.model_dump(), flush=True)
        await uow.commit()
        await uow.session.refresh(db_user)

    return db_user


@router.post(
    "/login",
    response_model=LoginSuccessSchema,
    summary="Login an existing user.",
    tags=["authentication"],
)
async def login(
    body: LoginSchema,
    unit_of_work: UnitOfWork = Depends(Provide[Container.unit_of_work]),
) -> User:
    """Login an existing user."""
    async with unit_of_work as uow:
        db_user = await uow.user.get_by_email(email=body.email)
    if not db_user:
        error = "Unable to find user with provided email."
        raise APIValidationError(error)
    if db_user and verify_password(
        plain_password=body.password,
        hashed_password=db_user.hashed_password,
    ):
        access_token = generate_access_token(user=db_user)
        db_user.access_token = access_token  # type: ignore[attr-defined]
        return db_user
    error = "Unable to login with provided credentials."
    raise APIValidationError(error)


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

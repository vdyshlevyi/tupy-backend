from logging import getLogger

from fastapi import APIRouter, Depends
from starlette import status

from app.api.authentication.utils import get_password_hash, get_request_user
from app.api.exceptions import ConflictError, NotFoundError
from app.api.users.schemas import AddUserSchema, UsersSchema, ViewProfileSchema
from app.dependencies.db import get_unit_of_work
from app.domain import User
from app.uow.unit_of_work import UnitOfWork

logger = getLogger(__name__)

router = APIRouter(prefix="/users", dependencies=[Depends(get_request_user)], tags=["users"])


@router.post(
    "",
    response_model=ViewProfileSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new users.",
)
async def create_user(
    body: AddUserSchema,
    uow: UnitOfWork = Depends(get_unit_of_work),
) -> dict:
    """Sign up for new users."""
    db_user = await uow.user.get_by_email(email=body.email)
    if db_user:
        error = "User with such email already exists."
        raise ConflictError(error)
    body_dict = body.model_dump()
    password = body_dict.pop("password")
    body_dict["hashed_password"] = get_password_hash(password)
    db_user = await uow.user.create(**body_dict, flush=True)
    await uow.commit()
    await uow.session.refresh(db_user)
    return db_user


@router.get(
    "",
    response_model=UsersSchema,
    summary="Get all users.",
    status_code=status.HTTP_200_OK,
)
async def get_all_users(uow: UnitOfWork = Depends(get_unit_of_work)) -> dict:
    """Get all users."""
    users = await uow.user.get_all()
    if not users:
        error = "No users found."
        raise NotFoundError(error)
    return {"items": users}


@router.get(
    "/profile",
    response_model=ViewProfileSchema,
    summary="View user's profile.",
    status_code=status.HTTP_200_OK,
)
async def view_profile(request_user: User = Depends(get_request_user)) -> User:
    """View user's profile."""
    logger.info(f"request_user is: {request_user}")
    # go to Redis and get cached user data
    return request_user


@router.get(
    "/user/{user_id}",
    response_model=ViewProfileSchema,
    summary="View user profile by ID.",
    status_code=status.HTTP_200_OK,
)
async def view_user_profile(user_id: int, uow: UnitOfWork = Depends(get_unit_of_work)) -> User:
    """View user profile by ID."""
    user = await uow.user.get_by_id(user_id)
    if not user:
        error = f"User with ID {user_id} does not exist."
        raise NotFoundError(error)
    return user

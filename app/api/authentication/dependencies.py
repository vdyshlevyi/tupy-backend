from datetime import UTC, datetime, timedelta
from logging import getLogger

import jwt
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext

from app.api.exceptions import UnauthorizedError
from app.config import Settings
from app.containers import Container
from app.domain import User
from app.uow.unit_of_work import UnitOfWork

auth_schema = HTTPBearer(auto_error=False)

logger = getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@inject
def generate_access_token(
    user: User,
    settings: Settings = Depends(Provide[Container.settings]),
) -> str:
    """Generate JWT token for user."""
    payload = {
        "user_id": user.id,
        "exp": datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXP_MINUTES),
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }
    return jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)


@inject
async def get_token_payload(
    token: HTTPAuthorizationCredentials = Depends(auth_schema),
    settings: Settings = Depends(Provide[Container.settings]),
) -> dict:
    """Verify user's access_token."""
    if not token or not token.credentials:
        raise UnauthorizedError
    try:
        return jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.InvalidTokenError:
        return {}


@inject
async def get_request_user(
    payload: dict = Depends(get_token_payload),
    unit_of_work: UnitOfWork = Depends(Provide[Container.unit_of_work]),
):
    user_id = payload.get("user_id")
    if not user_id:
        raise UnauthorizedError

    async with unit_of_work as uow:
        user = await uow.user.get_by_id(user_id=user_id)
    if not user:
        raise UnauthorizedError
    return user

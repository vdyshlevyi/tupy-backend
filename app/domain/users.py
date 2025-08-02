from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import UserRoles

from .base import IDOrmModel


class User(IDOrmModel):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRoles] = mapped_column(
        SQLAlchemyEnum(UserRoles),
        nullable=False,
        default=UserRoles.ADMIN.value,
        server_default=UserRoles.ADMIN.value,
    )

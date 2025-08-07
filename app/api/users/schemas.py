from pydantic import EmailStr
from pydantic.fields import Field

from app.domain.enums import UserRoles
from app.schemas import BaseSchema


class ViewProfileSchema(BaseSchema):
    """Schema for view profile."""

    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str


class AddUserSchema(BaseSchema):
    """Schema for adding a new user."""

    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    password: str = Field(..., description="User's password")
    role: UserRoles = Field(UserRoles.ADMIN, description="User's role, default is 'ADMIN'")


class UsersSchema(BaseSchema):
    """Base schema for paginated responses."""

    total: int = Field(..., description="Total number of items")
    items: list[ViewProfileSchema] = Field(..., description="List of items in the current page")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")

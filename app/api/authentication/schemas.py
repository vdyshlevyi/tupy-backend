from pydantic import EmailStr
from pydantic.fields import Field

from app.schemas import BaseSchema


class LoginSchema(BaseSchema):
    """Schema for user login."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class LoginSuccessSchema(BaseSchema):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    access_token: str


class ViewProfileSchema(BaseSchema):
    """Schema for view profile."""

    id: int
    email: EmailStr
    first_name: str
    last_name: str

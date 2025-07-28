from pydantic import EmailStr

from app.schemas import BaseSchema


class ViewProfileSchema(BaseSchema):
    """Schema for view profile."""

    id: int
    email: EmailStr
    first_name: str
    last_name: str

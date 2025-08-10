from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema for all schemas in the project."""

    __abstract__ = True

    model_config = ConfigDict(extra="forbid")  # select one of: ['allow', 'ignore', 'forbid']


class BasePaginationSchema(BaseSchema):
    """Base schema for paginated responses."""

    total: int = Field(..., description="Total number of items")
    items: list = Field(..., description="List of items in the current page")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")

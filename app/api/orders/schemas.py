from geoalchemy2 import WKTElement
from pydantic.fields import Field

from app.schemas import BasePaginationSchema, BaseSchema


class LatLngPoint(BaseSchema):
    """Schema for latitude/longitude point."""

    lat: float = Field(..., description="Latitude coordinate", ge=-90, le=90)
    lng: float = Field(..., description="Longitude coordinate", ge=-180, le=180)

    def to_wkt(self) -> WKTElement:
        return WKTElement(f"POINT({self.lng} {self.lat})", srid=4326)


class ViewOrderSchema(BaseSchema):
    """Schema for view order."""

    id: int
    name: str | None
    description: str | None
    distance_km: float | None
    duration_minutes: float | None


class AddOrderSchema(BaseSchema):
    """Schema for adding a new order."""

    name: str | None = Field(None, description="Order name")
    description: str | None = Field(None, description="Order description")
    start_point: LatLngPoint = Field(..., description="Start point coordinates")
    end_point: LatLngPoint = Field(..., description="End point coordinates")
    distance_km: float | None = Field(None, description="Order distance in kilometers")
    duration_minutes: float | None = Field(None, description="Order duration in minutes")


class OrdersSchema(BasePaginationSchema):
    """Base schema for order paginated responses."""

    items: list[ViewOrderSchema] = Field(..., description="List of orders in the current page")

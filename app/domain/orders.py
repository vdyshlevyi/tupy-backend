from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import IDOrmModel


class Order(IDOrmModel):
    __tablename__ = "orders"

    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_point: Mapped[Any] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    end_point: Mapped[Any] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    duration_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(),
        server_default=func.now(),
        nullable=False,
    )

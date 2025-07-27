from app.schemas import BaseSchema


class HealthCheckSchema(BaseSchema):
    message: str

from app.schemas import BaseSchema


class HealthCheckSchema(BaseSchema):
    result: str

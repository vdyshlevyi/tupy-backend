from app.schemas import BaseSchema


class InfoSchema(BaseSchema):
    title: str
    version: str

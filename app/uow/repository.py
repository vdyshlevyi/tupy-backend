from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class BaseModelRepository(SqlAlchemyRepository):
    def __init__(self, session: AsyncSession, model: type) -> None:
        super().__init__(session=session)
        self.model = model

from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session


class BaseModelRepository(SqlAlchemyRepository):
    def __init__(self, session: AsyncSession, model: type) -> None:
        super().__init__(session=session)
        self._model = model

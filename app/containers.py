from dependency_injector import containers, providers

from app.config import Settings
from app.uow.connection import AsyncSQLAlchemy
from app.uow.unit_of_work import UnitOfWork


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        # https://python-dependency-injector.ets-labs.org/wiring.html#wiring-configuration
        packages=["app"]
    )
    settings = providers.Singleton(Settings)
    db = providers.Singleton(AsyncSQLAlchemy, db_uri=settings.provided.DATABASE_URI)
    unit_of_work = providers.Factory(UnitOfWork, db=db.provided)

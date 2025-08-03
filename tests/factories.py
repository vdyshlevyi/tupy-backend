from datetime import datetime
from uuid import UUID

from factory.base import StubFactory
from factory.declarations import LazyFunction
from faker import Faker

from app.api.authentication.utils import get_password_hash
from app.domain.users import User
from app.uow.unit_of_work import UnitOfWork

fake = Faker()


class BaseFactory(StubFactory):
    @classmethod
    def build_dict(cls, **kwargs) -> dict:
        """Build a model dict from kwargs."""
        data = {}
        for key, value in cls.build(**kwargs).__dict__.items():
            # Remove
            if key == "_sa_instance_state":
                continue
            # Convert UUID -> str
            if isinstance(value, UUID):
                data[key] = str(value)
            else:
                data[key] = value
        return data

    @classmethod
    async def create_(cls, uow: UnitOfWork, **kwargs) -> User:
        """Async version of create method."""
        fields = cls.build_dict(**kwargs)
        for key, value in fields.items():
            if isinstance(value, datetime):
                fields[key] = value.replace(tzinfo=None)

        if "hashed_password" not in fields:
            fields["hashed_password"] = get_password_hash("123456")

        obj = cls._meta.model(**fields)
        uow.session.add(obj)
        await uow.session.commit()
        await uow.session.refresh(obj)
        return obj


class UserFactory(BaseFactory):
    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = User

    first_name = LazyFunction(lambda: fake.first_name())
    last_name = LazyFunction(lambda: fake.last_name())
    email = LazyFunction(lambda: fake.simple_profile().get("mail"))

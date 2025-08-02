import asyncio
from logging import getLogger

from app.api.authentication.utils import get_password_hash
from app.dependencies.db import get_unit_of_work

logger = getLogger(__name__)


async def main():
    gen = get_unit_of_work()
    uow = await gen.__anext__()  # retrieve the UnitOfWork instance
    admin_email = "admin@example.com"
    user_db_user = await uow.user.get_by_email(email=admin_email)
    if user_db_user:
        logger.info(f"Admin user with email '{admin_email}' already exists.")
        await gen.aclose()  # close the generator
        return
    hashed_password = get_password_hash("admin")
    await uow.user.create(
        email=admin_email,
        first_name="Admin",
        last_name="User",
        hashed_password=hashed_password,
    )
    await uow.commit()
    logger.info(f"Admin user with email '{admin_email}' created successfully.")
    await gen.aclose()  # close the generator


if __name__ == "__main__":
    asyncio.run(main())

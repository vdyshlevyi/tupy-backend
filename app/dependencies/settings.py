# @lru_cache
from app.config import Settings


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

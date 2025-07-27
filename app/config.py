from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TITLE: str = "Tupy Backend"
    VERSION: str = "0.0.1"
    HOST: str = "127.0.0.1"
    PORT: int = 9000
    DEBUG: bool = True
    SECRET_KEY: str  # WARNING! Set up via .env file or environment variable
    ORIGINS: tuple = ("http://localhost:3000", "http://localhost:8080")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# @lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]

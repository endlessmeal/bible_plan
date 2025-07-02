import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    PROJECT_NAME: str = "Bible Plan"
    VERSION: str = "1.0.0"

    BOT_TOKEN: str = "token"
    SQLITE_DB_PATH: str = "sqlite:///bible_plan.db"
    
    model_config = SettingsConfigDict(env_file=os.getenv("ENV_FILE", ".env"))


@lru_cache
def get_app_settings() -> Settings:
    """Возвращает настройки приложения."""
    return Settings()


def get_settings_no_cache() -> Settings:
    """Получение настроек без кеша."""
    return Settings()
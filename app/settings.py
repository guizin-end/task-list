from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_PASSWORD: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, gt=0)
    SECRET_KEY: str
    ALGORITHM: str

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str

    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    TODO_TRASH_EXPIRE_DAYS: int
    TODO_TRASH_CLEANUP_INTERVAL_DAYS: int


@lru_cache()
def get_settings() -> Settings:
    return Settings()

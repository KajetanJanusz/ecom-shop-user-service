from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Broker(StrEnum):
    KAFKA = "kafka"
    RABBIT = "rabbit"


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./memory"
    broker: Broker = Broker.KAFKA
    broker_url: str = "localhost:9092"
    group_id: str = "test-group"
    secret_key: str = Field(
        default="test-secret-key-must-be-at-least-32-characters-long", min_length=32
    )
    algorithm: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    return Settings()

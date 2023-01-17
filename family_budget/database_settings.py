import logging
from typing import Any

from pydantic import BaseSettings, Field
from sqlalchemy.engine import URL, Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import create_async_engine as aio_create_async_engine

logger = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    host: str = Field(default="localhost", env="PGHOST")
    port: int = Field(default=5432, env="PGPORT")  # noqa: WPS432
    username: str = Field(default="postgres", env="PGUSER")
    password: str | None = Field(env="PGPASSWORD")
    database: str = Field("postgres", env="PGDATABASE")
    drivername: str = Field("postgresql")

    @property
    def url(self) -> URL:
        params: dict[str, Any] = {
            "drivername": self.drivername,
            "host": self.host,
            "database": self.database,
            "username": self.username,
        }

        if self.password is not None:
            params["password"] = self.password

        if self.port is not None:
            params["port"] = self.port

        return URL.create(**params)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "."


def create_async_engine(settings: DatabaseSettings) -> AsyncEngine:
    logger.debug(
        "Creating a database engine with the connection string %s",
        settings.url.render_as_string(hide_password=True),
    )

    return aio_create_async_engine(settings.url)


def create_sync_engine(settings: DatabaseSettings) -> Engine:
    logger.debug(
        "Creating a database engine with the connection string %s",
        settings.url.render_as_string(hide_password=True),
    )

    return create_engine(settings.url)

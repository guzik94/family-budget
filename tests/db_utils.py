from family_budget.database_settings import DatabaseSettings, create_sync_engine
from family_budget.models import Base
from sqlalchemy import DDL
from sqlalchemy_utils import create_database, database_exists, drop_database


def _create_schema(connection):
    connection.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {Base.metadata.schema}"))


def recreate_schema(engine):
    with engine.connect() as connection:
        connection.execute(DDL(f"DROP SCHEMA {Base.metadata.schema} CASCADE"))
        _create_schema(connection)
        Base.metadata.create_all(connection)


def recreate_db(engine):
    if database_exists(settings.url):
        drop_database(settings.url)
    create_database(settings.url)

    with engine.begin() as connection:
        _create_schema(connection)
        Base.metadata.create_all(connection)


settings = DatabaseSettings()
settings.database = "test"
engine = create_sync_engine(settings)


__all__ = ["engine", "recreate_db", "recreate_schema"]

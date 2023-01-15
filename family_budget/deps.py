from family_budget.database_settings import DatabaseSettings, create_sync_engine
from fastapi import Depends
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_settings = DatabaseSettings()


def get_settings() -> DatabaseSettings:
    return _settings


_engine = create_sync_engine(_settings)


def get_engine() -> Engine:
    return _engine


_session_factory = sessionmaker(
    bind=_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_session_factory() -> sessionmaker:
    return _session_factory


class Context:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory


async def get_context(session_factory: sessionmaker = Depends(get_session_factory)) -> Context:
    return Context(session_factory)

from family_budget.database_settings import DatabaseSettings, create_sync_engine
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


def get_db():
    db = _session_factory()
    try:
        yield db
    finally:
        db.close()

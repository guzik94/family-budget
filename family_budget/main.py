from family_budget.app import get_app  # noqa
from family_budget.deps import get_engine
from family_budget.models import Base
from sqlalchemy import DDL


def create_tables():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {Base.metadata.schema}"))
        Base.metadata.create_all(conn)

    engine.dispose()


create_tables()

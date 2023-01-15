import logging

from family_budget.deps import get_engine
from family_budget.routers.auth import router as auth_router
from family_budget.routers.user import router as budget_router
from fastapi import FastAPI
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


def get_local_app(engine: Engine) -> FastAPI:
    local_app = FastAPI(
        title="family_budget",
    )

    @local_app.on_event("shutdown")
    def dispose_db_engine() -> None:
        logger.debug("Disposing the database engine")
        engine.dispose()

    local_app.include_router(router=budget_router)
    local_app.include_router(router=auth_router)

    return local_app


def get_app() -> FastAPI:
    engine = get_engine()
    return get_local_app(engine)

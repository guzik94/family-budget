import logging

from family_budget.deps import get_engine
from family_budget.routers import auth, budget, category, user
from fastapi import FastAPI
from fastapi_pagination import add_pagination
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

    local_app.include_router(router=auth.router)
    local_app.include_router(router=user.router)
    local_app.include_router(router=budget.router)
    local_app.include_router(router=category.router)

    return local_app


def get_app() -> FastAPI:
    engine = get_engine()
    return get_local_app(engine)


app = get_app()
add_pagination(app)

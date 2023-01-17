from family_budget.crud.category import query_categories
from family_budget.deps import get_db
from family_budget.schemas.category import Category
from fastapi import Depends
from fastapi.routing import APIRouter
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session
from starlette import status

router = APIRouter(prefix="/categories")


@router.get("/", tags=["get categories"], description="Get all categories", status_code=status.HTTP_200_OK)
def get_categories(session: Session = Depends(get_db)) -> Page[Category]:
    return paginate([Category(id=c.id, name=c.name) for c in query_categories(session)])

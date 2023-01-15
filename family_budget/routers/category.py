from family_budget.crud.category import query_categories
from family_budget.deps import Context, get_context
from family_budget.schemas.category import Category
from fastapi import Depends
from fastapi.routing import APIRouter
from starlette import status

router = APIRouter(prefix="/categories")


@router.get("/", tags=["get categories"], description="Get all categories", status_code=status.HTTP_200_OK)
async def get_categories(context: Context = Depends(get_context)):
    with context.session_factory.begin() as session:
        return [Category(name=c.name) for c in query_categories(session)]

from family_budget.auth.service import get_current_user
from family_budget.crud.budget import add_budget, query_budget, query_budgets, update_budget_income
from family_budget.deps import Context, get_context
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.budget import Budget, BudgetCreate
from family_budget.schemas.income import IncomeCreate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter

router = APIRouter(prefix="/budgets")


@router.post(
    "/", tags=["create budget"], description="Create budget for current user", status_code=status.HTTP_201_CREATED
)
async def create_budget(
    budget: BudgetCreate, current_user: UserInDB = Depends(get_current_user), context: Context = Depends(get_context)
) -> Budget:
    with context.session_factory.begin() as session:
        db_budget = add_budget(session, current_user.id, budget)
        return Budget.from_orm(db_budget)


@router.get("/", tags=["get budgets"], description="Get budgets for current user", status_code=status.HTTP_200_OK)
async def get_budgets(
    current_user: UserInDB = Depends(get_current_user), context: Context = Depends(get_context)
) -> list[Budget]:
    with context.session_factory.begin() as session:
        return [Budget.from_orm(b) for b in query_budgets(session, current_user.id)]


@router.put(
    "/{budget_id}/income", tags=["update income"], description="Update budget income", status_code=status.HTTP_200_OK
)
async def update_income(
    budget_id: int,
    income: IncomeCreate,
    current_user: UserInDB = Depends(get_current_user),
    context: Context = Depends(get_context),
) -> None:
    with context.session_factory.begin() as session:
        budget = query_budget(session, budget_id, current_user.id)
        if not budget:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
        update_budget_income(session, budget, income)

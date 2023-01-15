from family_budget.auth.service import get_current_user
from family_budget.crud.budget import add_budget, query_budgets
from family_budget.deps import Context, get_context
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.budget import Budget, BudgetCreate
from family_budget.schemas.expense import Expense
from family_budget.schemas.income import Income
from fastapi import Depends, status
from fastapi.routing import APIRouter

router = APIRouter(prefix="/budgets")


@router.post(
    "/", tags=["create budget"], description="Create budget for current user", status_code=status.HTTP_201_CREATED
)
async def create_budget(
    budget: BudgetCreate, current_user: UserInDB = Depends(get_current_user), context: Context = Depends(get_context)
) -> None:
    with context.session_factory.begin() as session:
        add_budget(session, current_user.id, budget)


@router.get("/", tags=["get budgets"], description="Get budgets for current user", status_code=status.HTTP_200_OK)
async def get_budgets(
    current_user: UserInDB = Depends(get_current_user), context: Context = Depends(get_context)
) -> list[Budget]:
    with context.session_factory.begin() as session:
        return [
            Budget(
                name=b.name,
                income=Income(name=b.income.name, amount=b.income.amount),
                expenses=[Expense(name=e.name, amount=e.amount, category=e.category.name) for e in b.expenses],
            )
            for b in query_budgets(session, current_user.id)
        ]

from family_budget.auth.service import get_current_user
from family_budget.crud.budget import (
    add_budget,
    add_budget_expense,
    delete_budget_expense,
    query_budget,
    query_budgets,
    update_budget_income,
)
from family_budget.crud.expense import query_expense
from family_budget.deps import Context, get_context
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.budget import Budget, BudgetCreate
from family_budget.schemas.expense import ExpenseCreate
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
) -> Budget:
    with context.session_factory.begin() as session:
        budget = query_budget(session, budget_id, current_user.id)
        if not budget:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
        budget = update_budget_income(budget, income)
        return Budget.from_orm(budget)


@router.post(
    "/{budget_id}/expenses/",
    tags=["add expense"],
    description="Add expense to budget",
    status_code=status.HTTP_201_CREATED,
)
async def add_expense(
    budget_id: int,
    expense: ExpenseCreate,
    current_user: UserInDB = Depends(get_current_user),
    context: Context = Depends(get_context),
) -> Budget:
    session = context.session_factory()
    budget = query_budget(session, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
    db_budget = add_budget_expense(session, budget, expense)
    return Budget.from_orm(db_budget)


@router.delete(
    "/{budget_id}/expenses/{expense_id}",
    tags=["delete expense"],
    description="Delete expense from budget",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_expense(
    budget_id: int,
    expense_id: int,
    current_user: UserInDB = Depends(get_current_user),
    context: Context = Depends(get_context),
) -> None:
    with context.session_factory.begin() as session:
        budget = query_budget(session, budget_id, current_user.id)
        if not budget:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
        budget_expense = query_expense(session, budget_id, expense_id)
        if not budget_expense:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Expense for this budget does not exist"
            )
        delete_budget_expense(session, budget, budget_expense)

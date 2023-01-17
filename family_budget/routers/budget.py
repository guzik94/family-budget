from family_budget.auth.service import get_current_user
from family_budget.crud.budget import (
    add_budget,
    add_budget_expense,
    add_shared_user,
    delete_budget_expense,
    query_budget,
    query_budgets,
    query_shared_budget,
    query_shared_budgets,
    update_budget_income,
)
from family_budget.crud.expense import query_expense
from family_budget.crud.user import query_user
from family_budget.deps import get_db
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.budget import Budget, BudgetCreate
from family_budget.schemas.expense import ExpenseCreate
from family_budget.schemas.income import IncomeCreate
from family_budget.schemas.user import UserShareCreate
from fastapi import Depends, HTTPException, status
from fastapi.routing import APIRouter
from fastapi_pagination import Page, paginate
from sqlalchemy.orm import Session

router = APIRouter(prefix="/budgets")


@router.post(
    "/", tags=["create budget"], description="Create budget for current user", status_code=status.HTTP_201_CREATED
)
async def create_budget(
    budget: BudgetCreate, current_user: UserInDB = Depends(get_current_user), session: Session = Depends(get_db)
) -> Budget:
    db_budget = add_budget(session, current_user.id, budget)
    return Budget.from_orm(db_budget)


@router.get("/", tags=["get budgets"], description="Get budgets for current user", status_code=status.HTTP_200_OK)
async def get_budgets(
    name_filter: str | None = None,
    category_filter: str | None = None,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Page[Budget]:
    own_budgets = [Budget.from_orm(b) for b in query_budgets(session, current_user.id, name_filter, category_filter)]
    budgets_shared_with_user = [
        Budget.from_orm(b) for b in query_shared_budgets(session, current_user.id, name_filter, category_filter)
    ]
    return paginate(own_budgets + budgets_shared_with_user)


@router.put(
    "/{budget_id}/income", tags=["update income"], description="Update budget income", status_code=status.HTTP_200_OK
)
async def update_income(
    budget_id: int,
    income: IncomeCreate,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Budget:
    budget = query_budget(session, budget_id, current_user.id)
    budget = budget or query_shared_budget(session, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
    budget = update_budget_income(session, budget, income)
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
    session: Session = Depends(get_db),
) -> Budget:
    budget = query_budget(session, budget_id, current_user.id)
    budget = budget or query_shared_budget(session, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
    budget = add_budget_expense(session, budget, expense)
    return Budget.from_orm(budget)


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
    session: Session = Depends(get_db),
) -> None:
    budget = query_budget(session, budget_id, current_user.id)
    budget = budget or query_shared_budget(session, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")
    budget_expense = query_expense(session, budget_id, expense_id)
    if not budget_expense:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Expense for this budget does not exist"
        )
    delete_budget_expense(session, budget, budget_expense)


@router.post(
    "/{budget_id}/share",
    tags=["share budget"],
    description="Share budget with a user",
    status_code=status.HTTP_201_CREATED,
)
async def share_budget(
    user: UserShareCreate,
    budget_id: int,
    current_user: UserInDB = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> Budget:
    budget = query_budget(session, budget_id, current_user.id)
    if not budget:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Budget does not exist")

    shared_user = query_user(session, user.username)
    if not shared_user:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Shared user does not exist")
    if shared_user in budget.shared_with:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Budget is already shared with user")

    budget = add_shared_user(session, budget, shared_user.id)
    return Budget.from_orm(budget)

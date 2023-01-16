from family_budget.crud.category import get_or_create_category
from family_budget.models.budget import Budget
from family_budget.models.expense import Expense
from family_budget.models.income import Income
from family_budget.schemas.budget import BudgetCreate
from family_budget.schemas.income import IncomeCreate
from sqlalchemy.orm import Session


def query_budgets(session: Session, user_id: int):
    return session.query(Budget).filter(Budget.user_id == user_id).all()


def query_budget(session: Session, budget_id: int, user_id: int):
    return session.query(Budget).filter(Budget.id == budget_id and Budget.user_id == user_id).first()


def add_budget(session: Session, user_id: int, budget: BudgetCreate):
    db_budget = Budget(
        name=budget.name,
        user_id=user_id,
        income=Income(name=budget.income.name, amount=budget.income.amount),
        expenses=[
            Expense(name=e.name, amount=e.amount, category=get_or_create_category(session, name=e.category))
            for e in budget.expenses
        ],
    )
    session.add(db_budget)
    session.flush()

    return db_budget


def update_budget_income(session, budget, income: IncomeCreate):
    budget.income.name = income.name
    budget.income.amount = income.amount
    session.commit()

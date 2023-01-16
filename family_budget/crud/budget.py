from family_budget.crud.category import get_or_create_category
from family_budget.models.budget import Budget
from family_budget.models.expense import Expense
from family_budget.models.income import Income
from family_budget.schemas.budget import BudgetCreate
from family_budget.schemas.expense import ExpenseCreate
from family_budget.schemas.income import IncomeCreate
from sqlalchemy.orm import Session


def query_budgets(session: Session, user_id: int) -> list[Budget]:
    return session.query(Budget).filter(Budget.user_id == user_id).all()


def query_budget(session: Session, budget_id: int, user_id: int) -> Budget:
    return session.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()


def add_budget(session: Session, user_id: int, budget: BudgetCreate) -> Budget:
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
    session.commit()
    session.refresh(db_budget)

    return db_budget


def update_budget_income(session, budget, income: IncomeCreate) -> Budget:
    budget.income.name = income.name
    budget.income.amount = income.amount

    session.commit()
    session.refresh(budget)

    return budget


def add_budget_expense(session, budget, expense: ExpenseCreate) -> Budget:
    budget.expenses.append(
        Expense(
            name=expense.name, amount=expense.amount, category=get_or_create_category(session, name=expense.category)
        )
    )
    session.commit()
    session.refresh(budget)
    return budget


def delete_budget_expense(session, budget, budget_expense):
    budget.expenses.remove(budget_expense)
    session.commit()
    session.refresh(budget)

    return budget

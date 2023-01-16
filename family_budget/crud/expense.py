from family_budget.models.expense import Expense
from sqlalchemy.orm import Session


def query_expense(session: Session, budget_id: int, expense_id: int) -> Expense:
    return session.query(Expense).filter(Expense.budget_id == budget_id, expense_id == expense_id).first()

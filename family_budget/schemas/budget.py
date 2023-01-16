from pydantic import BaseModel

from .base import SchemaBase
from .expense import Expense, ExpenseCreate
from .income import Income, IncomeCreate


class BudgetCreate(BaseModel):
    name: str
    income: IncomeCreate
    expenses: list[ExpenseCreate]


class Budget(SchemaBase):
    name: str
    income: Income
    expenses: list[Expense]

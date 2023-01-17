from pydantic import BaseModel

from .base import SchemaBase
from .expense import Expense, ExpenseCreate
from .income import Income, IncomeCreate


class BudgetCreate(BaseModel):
    name: str
    income: IncomeCreate
    expenses: list[ExpenseCreate]


class User(SchemaBase):
    id: int
    username: str


class BudgetSharedWithUser(SchemaBase):
    user: User


class Budget(SchemaBase):
    id: int
    name: str
    income: Income
    expenses: list[Expense]
    owner: User
    shared_with: list[BudgetSharedWithUser]

from pydantic import BaseModel

from .expense import Expense
from .income import Income


class BudgetCreate(BaseModel):
    name: str
    income: Income
    expenses: list[Expense]


class Budget(BaseModel):
    name: str
    income: Income
    expenses: list[Expense]

from pydantic import BaseModel

from .base import SchemaBase


class Category(SchemaBase):
    name: str


class Expense(SchemaBase):
    name: str
    amount: float
    category: Category


class ExpenseCreate(BaseModel):
    name: str
    amount: float
    category: str

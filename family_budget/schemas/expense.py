from pydantic import BaseModel

from .base import SchemaBase


class Category(SchemaBase):
    id: int
    name: str


class Expense(SchemaBase):
    id: int
    name: str
    amount: float
    category: Category


class ExpenseCreate(BaseModel):
    name: str
    amount: float
    category: str

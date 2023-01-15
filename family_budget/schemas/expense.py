from pydantic import BaseModel


class Expense(BaseModel):
    name: str
    amount: float
    category: str

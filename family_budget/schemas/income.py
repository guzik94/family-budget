from pydantic import BaseModel

from .base import SchemaBase


class Income(SchemaBase):
    id: int
    name: str
    amount: float


class IncomeCreate(BaseModel):
    name: str
    amount: float

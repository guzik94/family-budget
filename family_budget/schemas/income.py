from pydantic import BaseModel


class Income(BaseModel):
    name: str
    amount: float

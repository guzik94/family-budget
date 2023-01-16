from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base
from .category import Category


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    amount = Column(Float)
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    budget = relationship("Budget", back_populates="expenses", uselist=False)

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship(Category, back_populates="expenses", uselist=False)

    def __repr__(self):
        return f"Expense(name={self.name}, amount={self.amount}, budget_id={self.budget_id})"

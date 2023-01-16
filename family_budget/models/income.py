from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))
    amount = Column(Float)
    budget_id = Column(Integer, ForeignKey("budgets.id"))
    budget = relationship("Budget", back_populates="income", uselist=False)

    def __repr__(self):
        return f"Income(name={self.name}, amount={self.amount}, budget_id={self.budget_id})"

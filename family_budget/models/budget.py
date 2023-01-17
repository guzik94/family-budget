from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="budgets", uselist=False)

    income = relationship("Income", back_populates="budget", uselist=False)
    expenses = relationship("Expense", back_populates="budget", uselist=True)

    shared_with = relationship("BudgetSharedWithUsers", back_populates="budget", uselist=True)


class BudgetSharedWithUsers(Base):
    __tablename__ = "budget_shared_with_users"

    budget_id = Column(Integer, ForeignKey("budgets.id"), primary_key=True)
    budget = relationship("Budget", back_populates="shared_with")

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    user = relationship("User", back_populates="shared_budgets")

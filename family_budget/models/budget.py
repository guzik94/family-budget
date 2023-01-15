from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="budgets", uselist=False)

    income = relationship("Income", back_populates="budget", uselist=False)
    expenses = relationship("Expense", back_populates="budget", uselist=True)

    def __repr__(self):
        return f"Budget(name={self.name}, user_id={self.user_id})"

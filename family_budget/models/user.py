from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(32), unique=True)
    hashed_password = Column(String(80))
    budgets = relationship("Budget", back_populates="owner", uselist=True)
    shared_budgets = relationship("BudgetSharedWithUsers", back_populates="user")

    def __repr__(self) -> str:
        return f"User(username={self.username}"

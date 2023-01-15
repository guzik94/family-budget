from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    expense_id = Column(Integer, ForeignKey("expenses.id"))
    expense = relationship("Expense", back_populates="category", uselist=False)

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from . import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(32))

    expenses = relationship("Expense", back_populates="category", uselist=True)

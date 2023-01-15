from family_budget.models.category import Category
from sqlalchemy.orm import Session


def query_categories(session: Session):
    return session.query(Category).all()


def get_or_create_category(session: Session, name: str):
    category = session.query(Category).filter(Category.name == name).first()
    return category or Category(name=name)

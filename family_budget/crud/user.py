from family_budget.models.user import User
from sqlalchemy.orm import Session


def query_user(session: Session, username: str) -> User | None:
    return session.query(User).filter(User.username == username).first()


def add_user(session: Session, username: str, hashed_password: str) -> None:
    db_user = User(username=username, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()

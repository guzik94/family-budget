from family_budget.models.user import User
from sqlalchemy.orm import sessionmaker


def query_user(session_factory: sessionmaker, username: str) -> User | None:
    with session_factory.begin() as session:
        return session.query(User).filter(User.username == username).first()


def add_user(session_factory: sessionmaker, username: str, hashed_password: str) -> None:
    with session_factory.begin() as session:
        db_user = User(username=username, hashed_password=hashed_password)
        session.add(db_user)
        session.commit()

import pytest as pytest
from family_budget.app import app
from family_budget.auth.service import get_current_user, get_password_hash
from family_budget.crud.user import query_user
from family_budget.database_settings import DatabaseSettings, create_sync_engine
from family_budget.deps import get_db
from family_budget.models import Base
from family_budget.schemas.auth import UserInDB
from family_budget.schemas.budget import BudgetCreate
from family_budget.schemas.expense import ExpenseCreate
from family_budget.schemas.income import IncomeCreate
from family_budget.schemas.user import UserCreate
from fastapi.testclient import TestClient
from sqlalchemy import DDL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database


def recreate_schema(engine):
    with engine.connect() as connection:
        connection.execute(DDL(f"DROP SCHEMA {Base.metadata.schema} CASCADE"))
        connection.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {Base.metadata.schema}"))
        Base.metadata.create_all(connection)


def recreate_db(engine):
    if database_exists(settings.url):
        drop_database(settings.url)
    create_database(settings.url)

    with engine.begin() as conn:
        conn.execute(DDL(f"CREATE SCHEMA IF NOT EXISTS {Base.metadata.schema}"))
        Base.metadata.create_all(conn)


settings = DatabaseSettings()
settings.database = "test"
engine = create_sync_engine(settings)
recreate_db(engine)


session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return UserInDB(username="testuser", id=1, hashed_password=get_password_hash("testpassword"))


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def test_session():
    recreate_schema(engine)
    with session_factory.begin() as session:
        yield session


def budget_create_data():
    data = BudgetCreate(
        name="testbudget",
        income=IncomeCreate(name="testincome", amount=1.23),
        expenses=[ExpenseCreate(name="testexpense", amount=1.23, category="testcategory")],
    ).dict()
    return data


def test_create_user_and_assert_it_exists(client: TestClient, test_session: Session):
    username = "testuser"
    data = UserCreate(username=username, password="testpassword").dict()
    response = client.post("/users/", json=data)
    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": username}
    assert query_user(test_session, "testuser") is not None


def test_create_budget_and_assert_it_exists(client: TestClient, test_session: Session):
    data = UserCreate(username="testuser", password="testpassword").dict()
    client.post("/users/", json=data)

    response = client.post("/budgets/", json=budget_create_data())
    assert response.status_code == 201

    response = client.get("/budgets/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "testbudget",
            "income": {"id": 1, "name": "testincome", "amount": 1.23},
            "expenses": [
                {"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}
            ],
        }
    ]


def test_create_two_budgets(client: TestClient, test_session: Session):
    data = UserCreate(username="testuser", password="testpassword").dict()
    client.post("/users/", json=data)

    for _ in range(2):
        response = client.post("/budgets/", json=budget_create_data())
        assert response.status_code == 201

    response = client.get("/budgets/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "testbudget",
            "income": {"id": 1, "name": "testincome", "amount": 1.23},
            "expenses": [
                {"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}
            ],
        },
        {
            "id": 2,
            "name": "testbudget",
            "income": {"id": 2, "name": "testincome", "amount": 1.23},
            "expenses": [
                {"id": 2, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}
            ],
        },
    ]


def test_get_categories(client: TestClient, test_session: Session):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == []

    data = UserCreate(username="testuser", password="testpassword").dict()
    response = client.post("/users/", json=data)
    assert response.status_code == 201

    client.post("/budgets/", json=budget_create_data())
    client.post("/budgets/", json=budget_create_data())

    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "testcategory"}]


def test_create_budget_and_update_its_income(client: TestClient, test_session: Session):
    data = UserCreate(username="testuser", password="testpassword").dict()
    client.post("/users/", json=data)

    response = client.post("/budgets/", json=budget_create_data())
    budget_id = response.json()["id"]

    response = client.put(
        f"/budgets/{budget_id}/income", json=IncomeCreate(name="changed income name", amount=2.34).dict()
    )
    assert response.status_code == 200

    response = client.get("/budgets/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "testbudget",
            "income": {"id": 1, "name": "changed income name", "amount": 2.34},
            "expenses": [
                {"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}
            ],
        }
    ]


def test_create_budget_and_add_expense_to_it(client: TestClient, test_session: Session):
    data = UserCreate(username="testuser", password="testpassword").dict()
    client.post("/users/", json=data)

    response = client.post("/budgets/", json=budget_create_data())
    budget_id = response.json()["id"]

    response = client.post(
        f"/budgets/{budget_id}/expenses",
        json=ExpenseCreate(name="added expense", amount=2.34, category="testcategory").dict(),
    )
    assert response.status_code == 201

    response = client.get("/budgets/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "testbudget",
            "income": {"id": 1, "name": "testincome", "amount": 1.23},
            "expenses": [
                {"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}},
                {"id": 2, "name": "added expense", "amount": 2.34, "category": {"id": 1, "name": "testcategory"}},
            ],
        }
    ]


def test_create_budget_and_delete_its_expense(client: TestClient, test_session: Session):
    data = UserCreate(username="testuser", password="testpassword").dict()
    client.post("/users/", json=data)

    response = client.post("/budgets/", json=budget_create_data())
    budget_id = response.json()["id"]
    expense_id = response.json()["expenses"][0]["id"]
    assert response.status_code == 201

    response = client.delete(f"/budgets/{budget_id}/expenses/{expense_id}")
    assert response.status_code == 204
    assert response.text == ""

    response = client.get("/budgets/")
    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "testbudget",
            "income": {"id": 1, "name": "testincome", "amount": 1.23},
            "expenses": [],
        }
    ]

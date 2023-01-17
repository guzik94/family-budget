import pytest as pytest
from family_budget.app import app
from family_budget.deps import get_db
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from tests.db_utils import engine, recreate_db, recreate_schema

session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

recreate_db(engine)


@pytest.fixture()
def db_session():
    recreate_schema(engine)
    with session_factory.begin() as session:
        yield session


def override_get_db():
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def token_header_for_userdata(client, username, password):
    response = client.post(
        "/auth/token", data={"grant_type": "password", "username": f"{username}", "password": f"{password}"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.fixture
def token_header(client: TestClient):
    userdata = {"username": "testuser", "password": "testpassword"}
    response = client.post("/users/", json=userdata)
    assert response.status_code == 201
    return token_header_for_userdata(client, **userdata)

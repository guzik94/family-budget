from family_budget.crud.user import query_user
from family_budget.schemas.budget import BudgetCreate
from family_budget.schemas.expense import ExpenseCreate
from family_budget.schemas.income import IncomeCreate
from family_budget.schemas.user import UserCreate, UserShareCreate
from fastapi.testclient import TestClient


def budget_create_data():
    data = BudgetCreate(
        name="testbudget",
        income=IncomeCreate(name="testincome", amount=1.23),
        expenses=[ExpenseCreate(name="testexpense", amount=1.23, category="testcategory")],
    ).dict()
    return data


def token_header_for_userdata(client, username, password):
    response = client.post(
        "/auth/token", data={"grant_type": "password", "username": f"{username}", "password": f"{password}"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    return headers


userdata = UserCreate(**{"username": "testuser", "password": "testpassword"})


def budget_out():
    return {
        "id": 1,
        "name": "testbudget",
        "income": {"id": 1, "name": "testincome", "amount": 1.23},
        "expenses": [{"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}],
        "owner": {"id": 1, "username": "testuser"},
        "shared_with": [],
    }


def page(items):
    total = len(items)
    return {"items": items, "page": 1, "size": 50, "total": total}


def test_create_user_and_assert_it_exists(
    client: TestClient,
    db_session,
):
    response = client.post("/users/", json=userdata.dict())
    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": userdata.username}
    assert query_user(db_session, userdata.username) is not None


def test_create_budget_and_assert_it_exists(client: TestClient, db_session, token_header: dict):
    response = client.post("/budgets/", json=budget_create_data(), headers=token_header)
    assert response.status_code == 201

    response = client.get("/budgets/", headers=token_header)
    assert response.status_code == 200
    assert response.json() == page([budget_out()])


def test_create_two_budgets(client: TestClient, db_session, token_header: dict):
    for _ in range(2):
        response = client.post("/budgets/", json=budget_create_data(), headers=token_header)
        assert response.status_code == 201

    response = client.get("/budgets/", headers=token_header)
    assert response.status_code == 200
    assert response.json() == page(
        [
            budget_out(),
            {
                "id": 2,
                "name": "testbudget",
                "income": {"id": 2, "name": "testincome", "amount": 1.23},
                "expenses": [
                    {"id": 2, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}
                ],
                "owner": {"id": 1, "username": "testuser"},
                "shared_with": [],
            },
        ]
    )


def test_get_categories(client: TestClient, db_session, token_header: dict):
    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == page([])

    client.post("/budgets/", json=budget_create_data(), headers=token_header)
    client.post("/budgets/", json=budget_create_data(), headers=token_header)

    response = client.get("/categories/")
    assert response.status_code == 200
    assert response.json() == page([{"id": 1, "name": "testcategory"}])


def test_create_budget_and_update_its_income(client: TestClient, db_session, token_header: dict):
    response = client.post("/budgets/", json=budget_create_data(), headers=token_header)
    budget_id = response.json()["id"]

    response = client.put(
        f"/budgets/{budget_id}/income",
        json=IncomeCreate(name="changed income name", amount=2.34).dict(),
        headers=token_header,
    )
    assert response.status_code == 200

    response = client.get("/budgets/", headers=token_header)
    assert response.status_code == 200
    assert response.json() == page(
        [budget_out() | {"income": {"id": 1, "name": "changed income name", "amount": 2.34}}]
    )


def test_create_budget_and_add_expense_to_it(client: TestClient, db_session, token_header: dict):
    response = client.post("/budgets/", json=budget_create_data(), headers=token_header)
    budget_id = response.json()["id"]

    response = client.post(
        f"/budgets/{budget_id}/expenses",
        json=ExpenseCreate(name="added expense", amount=2.34, category="testcategory").dict(),
        headers=token_header,
    )
    assert response.status_code == 201

    response = client.get("/budgets/", headers=token_header)
    assert response.status_code == 200
    assert response.json() == page(
        [
            budget_out()
            | {
                "expenses": [
                    {"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}},
                    {"id": 2, "name": "added expense", "amount": 2.34, "category": {"id": 1, "name": "testcategory"}},
                ]
            }
        ]
    )


def test_create_budget_and_delete_its_expense(client: TestClient, db_session, token_header: dict):
    response = client.post("/budgets/", json=budget_create_data(), headers=token_header)
    budget_id = response.json()["id"]
    expense_id = response.json()["expenses"][0]["id"]
    assert response.status_code == 201

    response = client.delete(f"/budgets/{budget_id}/expenses/{expense_id}", headers=token_header)
    assert response.status_code == 204
    assert response.text == ""

    response = client.get("/budgets/", headers=token_header)
    assert response.status_code == 200
    assert response.json() == page([budget_out() | {"expenses": []}])


def test_create_budget_and_share_it(client: TestClient, db_session, token_header: dict):
    for data in (userdata.dict(), UserCreate(username="brother", password="testpassword").dict()):
        client.post("/users/", json=data)

    response = client.post("/budgets/", json=budget_create_data(), headers=token_header)
    budget_id = response.json()["id"]

    response = client.post(
        f"/budgets/{budget_id}/share", json=UserShareCreate(username="brother").dict(), headers=token_header
    )
    assert response.status_code == 201

    brother_token_header = token_header_for_userdata(client, "brother", "testpassword")
    response = client.get("/budgets/", headers=brother_token_header)
    assert response.status_code == 200
    assert response.json() == page(
        [
            {
                "id": 1,
                "name": "testbudget",
                "income": {"id": 1, "name": "testincome", "amount": 1.23},
                "expenses": [
                    {"id": 1, "name": "testexpense", "amount": 1.23, "category": {"id": 1, "name": "testcategory"}}
                ],
                "owner": {"id": 1, "username": "testuser"},
                "shared_with": [{"user": {"id": 2, "username": "brother"}}],
            }
        ]
    )


def test_create_budgets_and_filter_by_name(client: TestClient, db_session, token_header: dict):
    client.post("/budgets/", json=budget_create_data() | {"name": "A"}, headers=token_header)
    client.post("/budgets/", json=budget_create_data() | {"name": "B"}, headers=token_header)
    client.post("/budgets/", json=budget_create_data() | {"name": "C"}, headers=token_header)
    client.post("/budgets/", json=budget_create_data() | {"name": "ABC"}, headers=token_header)

    filter_length = [("A", 2), ("B", 2), ("C", 2), ("aB", 1), ("bc", 1), ("AC", 0)]

    for filter_value, expected_length in filter_length:
        response = client.get(f"/budgets/?name_filter={filter_value}", headers=token_header)
        assert len(response.json()["items"]) == expected_length


def test_create_budgets_and_filter_by_expense_category(client: TestClient, db_session, token_header: dict):
    categories = ["A", "B", "C", "ABC"]
    for category in categories:
        data = BudgetCreate(
            name="testbudget",
            income=IncomeCreate(name="testincome", amount=1.23),
            expenses=[ExpenseCreate(name="testexpense", amount=1.23, category=category)],
        ).dict()
        client.post("/budgets/", json=data, headers=token_header)

    filter_length = [("A", 2), ("B", 2), ("C", 2), ("aB", 1), ("bc", 1), ("AC", 0)]

    for filter_value, expected_length in filter_length:
        response = client.get(f"/budgets/?category_filter={filter_value}", headers=token_header)
        assert len(response.json()["items"]) == expected_length


def test_create_budgets_and_filter_by_name_and_expense_category(client: TestClient, db_session, token_header: dict):
    data = BudgetCreate(
        name="ABC",
        income=IncomeCreate(name="testincome", amount=1.23),
        expenses=[ExpenseCreate(name="testexpense", amount=1.23, category="ABC")],
    ).dict()
    client.post("/budgets/", json=data, headers=token_header)

    response = client.get("/budgets/?name_filter=A&category_filter=A", headers=token_header)
    assert len(response.json()["items"]) == 1

    response = client.get("/budgets/?name_filter=D&category_filter=A", headers=token_header)
    assert len(response.json()["items"]) == 0

    response = client.get("/budgets/?name_filter=A&category_filter=D", headers=token_header)
    assert len(response.json()["items"]) == 0

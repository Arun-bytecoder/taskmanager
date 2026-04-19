import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from db.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

USER = {"username": "testuser", "email": "test@example.com", "password": "testpass123"}


def get_token():
    client.post("/register", json=USER)
    resp = client.post("/login", data={"username": USER["username"], "password": USER["password"]})
    return resp.json()["access_token"]


def auth_headers():
    return {"Authorization": f"Bearer {get_token()}"}


# ── Auth tests ────────────────────────────────────────────────────────────────

def test_register():
    resp = client.post("/register", json=USER)
    assert resp.status_code == 201
    assert resp.json()["username"] == USER["username"]


def test_register_duplicate_username():
    client.post("/register", json=USER)
    resp = client.post("/register", json=USER)
    assert resp.status_code == 400


def test_login_success():
    client.post("/register", json=USER)
    resp = client.post("/login", data={"username": USER["username"], "password": USER["password"]})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password():
    client.post("/register", json=USER)
    resp = client.post("/login", data={"username": USER["username"], "password": "wrong"})
    assert resp.status_code == 401


# ── Task tests ────────────────────────────────────────────────────────────────

def test_create_task():
    headers = auth_headers()
    resp = client.post("/tasks", json={"title": "Buy milk", "description": "2% please"}, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["title"] == "Buy milk"
    assert resp.json()["completed"] is False


def test_get_tasks():
    headers = auth_headers()
    client.post("/tasks", json={"title": "Task 1"}, headers=headers)
    client.post("/tasks", json={"title": "Task 2"}, headers=headers)
    resp = client.get("/tasks", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_get_single_task():
    headers = auth_headers()
    created = client.post("/tasks", json={"title": "Single"}, headers=headers).json()
    resp = client.get(f"/tasks/{created['id']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Single"


def test_update_task():
    headers = auth_headers()
    created = client.post("/tasks", json={"title": "Old title"}, headers=headers).json()
    resp = client.put(f"/tasks/{created['id']}", json={"title": "New title", "completed": True}, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "New title"
    assert resp.json()["completed"] is True


def test_delete_task():
    headers = auth_headers()
    created = client.post("/tasks", json={"title": "Delete me"}, headers=headers).json()
    resp = client.delete(f"/tasks/{created['id']}", headers=headers)
    assert resp.status_code == 204
    resp = client.get(f"/tasks/{created['id']}", headers=headers)
    assert resp.status_code == 404


def test_filter_completed():
    headers = auth_headers()
    t1 = client.post("/tasks", json={"title": "Done"}, headers=headers).json()
    client.post("/tasks", json={"title": "Pending"}, headers=headers)
    client.put(f"/tasks/{t1['id']}", json={"completed": True}, headers=headers)
    resp = client.get("/tasks?completed=true", headers=headers)
    assert resp.json()["total"] == 1


def test_pagination():
    headers = auth_headers()
    for i in range(15):
        client.post("/tasks", json={"title": f"Task {i}"}, headers=headers)
    resp = client.get("/tasks?page=1&page_size=5", headers=headers)
    data = resp.json()
    assert len(data["tasks"]) == 5
    assert data["total"] == 15
    assert data["total_pages"] == 3


def test_task_isolation():
    """User A cannot see User B's tasks."""
    client.post("/register", json={"username": "userA", "email": "a@a.com", "password": "passA"})
    client.post("/register", json={"username": "userB", "email": "b@b.com", "password": "passB"})

    tok_a = client.post("/login", data={"username": "userA", "password": "passA"}).json()["access_token"]
    tok_b = client.post("/login", data={"username": "userB", "password": "passB"}).json()["access_token"]

    task = client.post("/tasks", json={"title": "Secret"}, headers={"Authorization": f"Bearer {tok_a}"}).json()
    resp = client.get(f"/tasks/{task['id']}", headers={"Authorization": f"Bearer {tok_b}"})
    assert resp.status_code == 404

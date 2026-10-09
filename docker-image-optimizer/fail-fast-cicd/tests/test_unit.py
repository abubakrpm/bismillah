"""Fast unit tests: run in-process with Flask's test client, no container needed."""

import pytest

from app.main import TASKS, app


@pytest.fixture
def client():
    TASKS.clear()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_create_task(client):
    res = client.post("/tasks", json={"title": "Write Dockerfile"})
    assert res.status_code == 201
    assert res.get_json() == {"id": 1, "title": "Write Dockerfile", "done": False}


def test_create_task_requires_title(client):
    res = client.post("/tasks", json={})
    assert res.status_code == 400


def test_create_task_rejects_long_title(client):
    res = client.post("/tasks", json={"title": "x" * 101})
    assert res.status_code == 400


def test_complete_task(client):
    client.post("/tasks", json={"title": "Set up pipeline"})
    res = client.patch("/tasks/1")
    assert res.status_code == 200
    assert res.get_json()["done"] is True


def test_complete_missing_task(client):
    res = client.patch("/tasks/999")
    assert res.status_code == 404

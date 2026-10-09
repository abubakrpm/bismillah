"""Integration tests: hit the REAL running container over HTTP.

Skipped unless APP_URL is set, so `pytest` locally only runs unit tests.
The pipeline sets APP_URL after starting the built image.
"""

import os

import pytest
import requests

APP_URL = os.getenv("APP_URL")

pytestmark = pytest.mark.skipif(not APP_URL, reason="APP_URL not set")


def test_container_health():
    res = requests.get(f"{APP_URL}/health", timeout=5)
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_task_lifecycle_against_container():
    created = requests.post(f"{APP_URL}/tasks", json={"title": "integration"}, timeout=5)
    assert created.status_code == 201
    task_id = created.json()["id"]

    done = requests.patch(f"{APP_URL}/tasks/{task_id}", timeout=5)
    assert done.status_code == 200
    assert done.json()["done"] is True

    listed = requests.get(f"{APP_URL}/tasks", timeout=5).json()
    assert any(t["id"] == task_id for t in listed)

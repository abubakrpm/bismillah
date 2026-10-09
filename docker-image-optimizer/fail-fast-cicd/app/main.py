"""Small task-tracker API used to demonstrate a fail-fast CI/CD pipeline."""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)

TASKS: list[dict] = []


@app.get("/health")
def health():
    return jsonify(status="ok", version=os.getenv("APP_VERSION", "dev"))


@app.get("/tasks")
def list_tasks():
    return jsonify(TASKS)


@app.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    if not title:
        return jsonify(error="title is required"), 400
    if len(title) > 100:
        return jsonify(error="title must be 100 characters or fewer"), 400

    task = {"id": len(TASKS) + 1, "title": title, "done": False}
    TASKS.append(task)
    return jsonify(task), 201


@app.patch("/tasks/<int:task_id>")
def complete_task(task_id: int):
    for task in TASKS:
        if task["id"] == task_id:
            task["done"] = True
            return jsonify(task)
    return jsonify(error="task not found"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))

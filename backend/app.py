"""Tiny task API for a DevOps practical: Flask + PostgreSQL."""
import os
import socket

import psycopg
from psycopg.rows import dict_row
from flask import Flask, jsonify, request

app = Flask(__name__)


def db_connection():
    """The Compose service 'db' is resolvable as a hostname on the backend network."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        dbname=os.getenv("DB_NAME", "taskmanager"),
        user=os.getenv("DB_USER", "taskuser"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=5,
        row_factory=dict_row,
    )


@app.get("/health")
def health():
    """AWS target-group health check: return HTTP 200 only if the database works."""
    try:
        with db_connection() as conn:
            conn.execute("SELECT 1")
        return jsonify(status="200", host=socket.gethostname()), 200
    except psycopg.Error:
        app.logger.exception("Database health check failed")
        return jsonify(status="unhealthy"), 503


@app.get("/api/tasks")
def list_tasks():
    with db_connection() as conn:
        tasks = conn.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
    return jsonify(tasks)


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict) or not isinstance(payload.get("title"), str):
        return jsonify(error="Please provide a task title."), 400
    title = payload["title"].strip()
    if not (1 <= len(title) <= 120):
        return jsonify(error="Task title must be 1–120 characters."), 400

    with db_connection() as conn:
        task = conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) "
            "RETURNING id, title, completed",
            (title,),
        ).fetchone()
    return jsonify(task), 201


@app.patch("/api/tasks/<int:task_id>")
def toggle_task(task_id):
    with db_connection() as conn:
        task = conn.execute(
            "UPDATE tasks SET completed = NOT completed WHERE id = %s "
            "RETURNING id, title, completed",
            (task_id,),
        ).fetchone()
    if task is None:
        return jsonify(error="Task not found."), 404
    return jsonify(task)


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    with db_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,)
        ).fetchone()
    if deleted is None:
        return jsonify(error="Task not found."), 404
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

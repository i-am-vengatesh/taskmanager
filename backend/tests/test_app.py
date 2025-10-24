# backend/tests/test_api.py
from fastapi.testclient import TestClient
from app import app, tasks  # import the FastAPI app object and tasks list

client = TestClient(app)

def setup_function():
    # Reset shared tasks list before each test
    tasks.clear()

def test_get_empty_tasks():
    resp = client.get("/")
    assert resp.status_code == 200
    # TemplateResponse returns HTML; TestClient returns text body
    assert "Task Manager" in resp.text
    assert "Current Tasks" in resp.text

def test_add_task_via_api():
    # add a task via form POST
    resp = client.post("/add", data={"task_name": "ci-demo-task"})
    assert resp.status_code == 200
    # response might be JSON or string depending on your handler; if JSON:
    try:
        body = resp.json()
        assert "Task" in str(body) or "message" in body
    except ValueError:
        # fallback to text check
        assert "added" in resp.text.lower() or "success" in resp.text.lower()

    # Now fetch the root page and check task present
    resp2 = client.get("/")
    assert resp2.status_code == 200
    assert "ci-demo-task" in resp2.text

def test_remove_task_via_api():
    # Add then remove
    client.post("/add", data={"task_name": "to-remove"})
    resp = client.post("/remove", data={"task_name": "to-remove"})
    assert resp.status_code == 200
    # Ensure task removed
    resp2 = client.get("/")
    assert "to-remove" not in resp2.text

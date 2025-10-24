# backend/tests/test_app.py

from logic import add_task, remove_task, get_tasks

def test_add_task():
    tasks = []
    add_task(tasks, "Write Jenkinsfile")
    assert tasks == ["Write Jenkinsfile"]

def test_remove_task():
    tasks = ["Write Jenkinsfile"]
    remove_task(tasks, "Write Jenkinsfile")
    assert tasks == []

def test_get_tasks():
    tasks = ["Task 1", "Task 2"]
    assert get_tasks(tasks) == ["Task 1", "Task 2"]

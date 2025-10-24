from fastapi import FastAPI, Request
from logic import add_task, remove_task, get_tasks

app = FastAPI()
tasks = []

@app.get("/")
async def read_tasks():
    return {"tasks": tasks}

@app.post("/add")
async def add_task_ui(request: Request):
    form = await request.form()
    task_name = form.get("task_name")
    add_task(tasks, task_name)
    return {"message": "added"}

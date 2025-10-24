# backend/app.py

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI(title="Task Manager")

tasks = []

# Setup templates folder
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_tasks(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "tasks": tasks})

@app.post("/add")
def add_task_ui(task_name: str = Form(...)):
    tasks.append(task_name)
    return {"message": f"Task '{task_name}' added successfully!"}

@app.post("/remove")
def remove_task_ui(task_name: str = Form(...)):
    if task_name in tasks:
        tasks.remove(task_name)
        return {"message": f"Task '{task_name}' removed successfully!"}
    return {"message": f"Task '{task_name}' not found."}

# Optional: API endpoints for testing
def add_task_logic(task_list, task_name):
    task_list.append(task_name)
    return task_list

def remove_task_logic(task_list, task_name):
    if task_name in task_list:
        task_list.remove(task_name)
    return task_list

def get_tasks_logic(task_list):
    return task_list

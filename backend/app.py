# backend/app.py

def add_task(tasks, task_name):
    """Add a task to the list"""
    tasks.append(task_name)
    return tasks

def remove_task(tasks, task_name):
    """Remove a task from the list"""
    if task_name in tasks:
        tasks.remove(task_name)
    return tasks

def get_tasks(tasks):
    """Return the list of tasks"""
    return tasks

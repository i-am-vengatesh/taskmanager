# backend/logic.py
def add_task(tasks, task_name):
    tasks.append(task_name)
    return tasks

def remove_task(tasks, task_name):
    if task_name in tasks:
        tasks.remove(task_name)
    return tasks

def get_tasks(tasks):
    return tasks

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

tasks = [
    {
        "id": 1,
        "title": "Finish internship assignment",
        "done": False
    },
    {
        "id": 2,
        "title": "Read a book",
        "done": False
    },
    {
        "id": 3,
        "title": "Watch a movie",
        "done": True
    }
]

class TaskCreate(BaseModel):
    title: str


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    raise HTTPException(status_code=404, detail=f"Task {id} not found")

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    new_id = max(existing_task["id"] for existing_task in tasks) + 1 if tasks else 1

    new_task = {
        "id": new_id,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task
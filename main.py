from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import create_database, get_connection

create_database()

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
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


@app.get("/", description="Returns basic information about the API task.")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", description="Checks whether the API is running.")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks", description="Returns a list of all tasks.")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        }
        for row in rows
    ]


@app.get("/tasks/{id}", description="Returns a specific task by its ID.")
def get_task(id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task {id} not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }



@app.post("/tasks", status_code=201, description="Creates a new task.")
def create_task(task: TaskCreate):
    if task.title is None or not task.title.strip():
        raise HTTPException(
            status_code=400,
            detail="Title is required and cannot be empty"
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title, 0)
    )

    new_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "id": new_id,
        "title": task.title,
        "done": False
    }


@app.put("/tasks/{id}", description="Updates an existing task.")
def update_task(id: int, task_update: TaskUpdate):
    for task in tasks:
        if task["id"] == id:
            if task_update.title is not None:
                if not task_update.title.strip():
                    raise HTTPException(
                        status_code=400,
                        detail="Title cannot be empty"
                    )
                task["title"] = task_update.title

            if task_update.done is not None:
                task["done"] = task_update.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )


@app.delete("/tasks/{id}", status_code=204, description="Deletes a task.")
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {id} not found"
    )
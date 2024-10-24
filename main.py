from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

app = FastAPI(title="TODO API", description="A simple TODO API built with FastAPI")

# Pydantic models for request/response
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = 1  # 1 (low) to 5 (high)

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    created_at: datetime
    completed: bool = False

    class Config:
        from_attributes = True

# In-memory storage
todos = {}
todo_id_counter = 1

@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate):
    global todo_id_counter

    new_todo = Todo(
        id=todo_id_counter,
        created_at=datetime.now(),
        **todo.dict()
    )

    todos[todo_id_counter] = new_todo
    todo_id_counter += 1

    return new_todo

@app.get("/todos/", response_model=List[Todo])
async def list_todos(completed: Optional[bool] = None):
    if completed is None:
        return list(todos.values())
    return [todo for todo in todos.values() if todo.completed == completed]

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    return todos[todo_id]

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoBase):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )

    todos[todo_id] = Todo(
        id=todo_id,
        created_at=todos[todo_id].created_at,
        completed=todos[todo_id].completed,
        **todo.dict()
    )

    return todos[todo_id]

@app.patch("/todos/{todo_id}/complete", response_model=Todo)
async def complete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )

    todos[todo_id].completed = True
    return todos[todo_id]

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )

    del todos[todo_id]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

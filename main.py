from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///data/todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class TodoModel(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(Integer, default=1)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request/response
class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = 1

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    created_at: datetime
    completed: bool

    class Config:
        from_attributes = True

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="TODO API", description="A simple TODO API built with FastAPI and SQLite")

@app.post("/todos/", response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(
        title=todo.title,
        description=todo.description,
        due_date=todo.due_date,
        priority=todo.priority
    )

    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo

@app.get("/todos/", response_model=List[Todo])
async def list_todos(
    completed: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(TodoModel)
    if completed is not None:
        query = query.filter(TodoModel.completed == completed)

    return query.offset(skip).limit(limit).all()

@app.get("/todos/{todo_id}", response_model=Todo)
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoBase, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )

    for key, value in todo.dict(exclude_unset=True).items():
        setattr(db_todo, key, value)

    db.commit()
    db.refresh(db_todo)

    return db_todo

@app.patch("/todos/{todo_id}/complete", response_model=Todo)
async def complete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )

    db_todo.completed = True
    db.commit()
    db.refresh(db_todo)

    return db_todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TODO item not found"
        )

    db.delete(db_todo)
    db.commit()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

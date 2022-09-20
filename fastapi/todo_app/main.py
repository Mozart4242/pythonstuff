from typing import Optional
from unittest.mock import NonCallableMagicMock
from fastapi import FastAPI, Depends, HTTPException
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from httpexceptions import *
from pydantic import BaseModel, Field
from auth import get_current_user, user_exception


models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class Todos(BaseModel):
    title: str
    description: Optional[str]
    priority: int = Field(gt=0,lt=11, description="0 to 10")
    complete: bool




@app.get("/")
async def read_all(db: Session = Depends(get_db)):
    return db.query(models.Todos).all()


@app.get("/users/todo")
async def read_by_user(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise user_exception()
    return db.query(models.Todos).filter(models.Todos.owner_id == user.get("id")).all()
 
   
@app.get("/todos/{todo_id}")
async def get_todo_by_id(todo_id: int, user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise user_exception()

    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()
    if todo_model is not None:
        return todo_model
    raise error_404()


@app.post("/")
async def create_todo(todo: Todos,user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise user_exception()

    todo_model = models.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete
    todo_model.owner_id = user.get("id")
    
    db.add(todo_model)
    db.commit()
    return {"Status": "Create Succeed"}


@app.put("/{todo_id}")
async def update_todo(todo_id: int, todo: Todos,user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    if user is None:
        raise user_exception()
        
    todo_model = db.query(models.Todos).filter(models.Todos.id == todo_id).filter(models.Todos.owner_id == user.get("id")).first()   
    if todo_model is None:
        raise error_404()    
    db.add(todo_model)
    db.commit()
    return {"Status": "Update Succeed"}
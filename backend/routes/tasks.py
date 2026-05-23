from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas import TaskCreate, TaskUpdate, TaskResponse
from backend.routes.users import get_current_user
from backend.crud import tasks as crud_tasks

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
        task: TaskCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return crud_tasks.create_task(db=db, task_schemas=task, user_id=current_user.id)

@router.get("/tasks", response_model=list[TaskResponse])
def get_tasks(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
        done: bool | None = Query(default=None),
        search: str | None = Query(default=None, max_length=100),
        limit: int = Query(default=100, ge=1, le=100),
        offset: int = Query(default=0, ge=0)
):
    return crud_tasks.get_tasks(
        db=db,
        user_id=current_user.id,
        done=done,
        search=search,
        limit=limit,
        offset=offset
    )

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = crud_tasks.get_task(db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = crud_tasks.update_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id,
        task_data=task_data
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(
        task_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    success = crud_tasks.delete_task(db, task_id=task_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return None

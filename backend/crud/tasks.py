from sqlalchemy.orm import Session
from backend.models import Task
from backend.schemas import TaskCreate, TaskUpdate

def get_task(db: Session, task_id: int, user_id: int):
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

def get_tasks(
        db: Session,
        user_id: int,
        done: bool = None,
        search: str = None,
        limit: int = 100,
        offset: int = 0
):
    query = db.query(Task).filter(Task.user_id == user_id)
    if done is not None:
        query = query.filter(Task.done.is_(done))
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))
    return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()

def create_task(
        db: Session,
        task_schemas: TaskCreate,
        user_id: int
):
    new_task = Task(
        title=task_schemas.title,
        description=task_schemas.description,
        done=task_schemas.done,
        user_id=user_id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

def delete_task(db: Session, task_id: int, user_id: int):
    task = get_task(db, task_id, user_id)
    if task:
        db.delete(task)
        db.commit()
        return True
    return False

def update_task(
        db: Session,
        task_id: int,
        user_id: int,
        task_data: TaskUpdate
):
    task = get_task(db, task_id, user_id)
    if not task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)
    return task
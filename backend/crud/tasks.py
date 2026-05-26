from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models import Task
from backend.schemas import TaskCreate, TaskUpdate

async def get_task(db: AsyncSession, task_id: int, user_id: int):
    result = await db.execute(select(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ))
    return result.scalars().first()

async def get_tasks(
        db: AsyncSession,
        user_id: int,
        done: bool = None,
        search: str = None,
        limit: int = 100,
        offset: int = 0
):
    query = select(Task).filter(Task.user_id == user_id)
    if done is not None:
        query = query.filter(Task.done.is_(done))
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_task(
        db: AsyncSession,
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
    await db.commit()
    await db.refresh(new_task)
    return new_task

async def delete_task(db: AsyncSession, task_id: int, user_id: int):
    task = await get_task(db, task_id, user_id)
    if task:
        await db.delete(task)
        await db.commit()
        return True
    return False

async def update_task(
        db: AsyncSession,
        task_id: int,
        user_id: int,
        task_data: TaskUpdate
):
    task = await get_task(db, task_id, user_id)
    if not task:
        return None

    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task
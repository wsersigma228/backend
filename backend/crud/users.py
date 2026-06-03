from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.models import User
from backend.schemas import UserCreate
from backend.security import get_password_hash

async def get_user_by_username(db: AsyncSession, username: str):
    """Retrieve user by exact username match."""
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def get_all_users(db: AsyncSession):
    result = await db.execute(select(User))
    return result.scalars().all()

async def create_user(db: AsyncSession, user_schemas: UserCreate):
    """Create a new user with hashed password."""
    hashed_password = get_password_hash(user_schemas.password)
    new_user = User(
        username=user_schemas.username,
        email=user_schemas.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if db_user:
        await db.delete(db_user)
        await db.commit()
        return True
    return False
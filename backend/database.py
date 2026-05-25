from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from backend.config import DATABASE_URL

# Convert sync DATABASE_URL (postgresql+psycopg://) to async (postgresql+psycopg_async://)
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg_async://")

engine = create_async_engine(ASYNC_DATABASE_URL)
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=AsyncSession)
Base = declarative_base()


async def get_db():
    async with SessionLocal() as db:
        yield db

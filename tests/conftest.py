import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.main import api
from backend.database import get_db, Base
from backend.config import DATABASE_URL
from backend.models import User
from backend.routes.users import get_current_user


TEST_DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+psycopg_async://").replace("/mydb", "/test_db")


test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_db():
    """Create and drop database tables for each test to ensure isolation."""

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

async def override_get_db():
    """Override the dependency to use the isolated test database."""
    async with TestingSessionLocal() as session:
        yield session

api.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def async_client():
    """Provide an asynchronous HTTP client for anonymous requests."""

    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="function")
async def auth_client():
    """Provide an asynchronous HTTP client with an authenticated mock user."""
    mock_user = User(username="tester", email="test@example.com", hashed_password="fake", role="user")
    
    async with TestingSessionLocal() as session:
        session.add(mock_user)
        await session.commit()
        await session.refresh(mock_user)

    api.dependency_overrides[get_current_user] = lambda: mock_user
    
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
        
    api.dependency_overrides.pop(get_current_user, None)

from unittest.mock import patch, AsyncMock
import pytest

@pytest.fixture(autouse=True)
def mock_redis():
    """Mock Redis to prevent event loop closure errors during isolated async tests."""
    with patch("backend.routes.tasks.redis_client.delete", new_callable=AsyncMock):
        with patch("backend.routes.users.redis_client.delete", new_callable=AsyncMock):
            yield

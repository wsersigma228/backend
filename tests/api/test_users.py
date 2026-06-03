import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_user_success(async_client: AsyncClient):
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }

    response = await async_client.post("/users", json=user_data)

    assert response.status_code == 201

    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data

async def test_create_user_duplicate_username(async_client: AsyncClient):
    user_data = {
        "username": "testuser",
        "password": "securepassword123"
    }

    response1 = await async_client.post("/users", json=user_data)
    assert response1.status_code == 201

    response2 = await async_client.post("/users", json=user_data)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Username already exists"

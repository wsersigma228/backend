import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_login_success(async_client: AsyncClient):
    user_data = {"username": "loginuser", "password": "mypassword"}
    await async_client.post("/users", json=user_data)

    login_data = {
        "username": "loginuser",
        "email": "",
        "password": "mypassword"
    }
    response = await async_client.post("/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

async def test_login_wrong_password(async_client: AsyncClient):
    user_data = {"username": "loginuser2", "password": "mypassword"}
    await async_client.post("/users", json=user_data)

    login_data = {
        "username": "loginuser2",
        "email": "",
        "password": "wrongpassword!"
    }
    response = await async_client.post("/login", json=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Wrong password"

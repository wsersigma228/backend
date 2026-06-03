import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_task(auth_client: AsyncClient):
    task_data = {
        "title": "My first task",
        "description": "It works!"
    }

    response = await auth_client.post("/tasks", json=task_data)

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert "id" in data


async def test_get_task(auth_client: AsyncClient):
    create_resp = await auth_client.post("/tasks", json={
        "title": "Task to get",
        "description": "I need to read this"
    })
    task_id = create_resp.json()["id"]

    get_resp = await auth_client.get(f"/tasks/{task_id}")

    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == task_id
    assert data["title"] == "Task to get"


async def test_delete_task(auth_client: AsyncClient):
    create_resp = await auth_client.post("/tasks", json={
        "title": "Task to delete",
        "description": "I need to read this"
    })
    task_id = create_resp.json()["id"]

    delete_resp = await auth_client.delete(f"/tasks/{task_id}")
    assert delete_resp.status_code == 204

    get_resp = await auth_client.get(f"/tasks/{task_id}")
    assert get_resp.status_code == 404

async def test_update_task(auth_client: AsyncClient):
    create_resp = await auth_client.post("/tasks", json={
        "title": "Old title",
        "description": "Old description"
    })
    task_id = create_resp.json()["id"]

    update_resp = await auth_client.put(f"/tasks/{task_id}", json={
        "title": "New title",
        "description": "New description",
        "done": True
    })

    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["title"] == "New title"
    assert data["description"] == "New description"
    assert data["done"] == True

async def test_get_tasks_list(auth_client: AsyncClient):
    await auth_client.post("/tasks", json={"title": "Task 1", "description": "First"})
    await auth_client.post("/tasks", json={"title": "Task 2", "description": "Second"})

    response = await auth_client.get("/tasks")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)

    assert len(data) == 2

    title = [task["title"] for task in data]
    assert "Task 1" in title
    assert "Task 2" in title
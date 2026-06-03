from fastapi import FastAPI
from backend.routes import tasks, users

api = FastAPI()

api.include_router(tasks.router)
api.include_router(users.router)


@api.get("/")
def home():
    """Health check endpoint to verify the API is running."""
    return {"ok": True}

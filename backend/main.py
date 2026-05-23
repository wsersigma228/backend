from fastapi import FastAPI
from backend.routes import tasks, users

api = FastAPI()

api.include_router(tasks.router)
api.include_router(users.router)


@api.get("/")
def home():
    return {"ok": True}

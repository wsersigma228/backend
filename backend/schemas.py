from pydantic import BaseModel, Field
from datetime import datetime


# TASKCONFIG
class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    done: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=300)
    done: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    done: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# USERCONFIG
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=4, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str

    class Config:
        from_attributes = True

class UserWithTasksResponse(UserResponse):
    tasks: list[TaskResponse] = []


class UserLogin(BaseModel):
    username: str
    email: str
    password: str


# TOKEN
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

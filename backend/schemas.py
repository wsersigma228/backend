from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# TASKCONFIG
class TaskCreate(BaseModel):
    """Schema for creating a new task."""
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

    model_config = ConfigDict(from_attributes=True)


# USERCONFIG
class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str = Field(min_length=3, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=4, max_length=100)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserWithTasksResponse(UserResponse):
    tasks: list[TaskResponse] = []


class UserLogin(BaseModel):
    username: str
    password: str


# TOKEN
class Token(BaseModel):
    """Auth token payload."""
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefreshRequest(BaseModel):
    refresh_token: str

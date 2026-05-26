from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import jwt, ExpiredSignatureError, JWTError

from backend.config import SECRET_KEY, ALGORITHM
from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, UserResponse, UserLogin, Token, UserWithTasksResponse, TokenRefreshRequest
from backend.security import create_access_token, create_refresh_token, get_current_user, get_current_admin, verify_password, security
from backend.crud import users as crud_users

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    return await crud_users.create_user(db=db, user_schemas=user)

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud_users.get_user_by_username(db, username=user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Wrong password")

    token_data = {
        "sub": db_user.username,
        "email": db_user.email,
        "user_id": db_user.id
    }
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", response_model=Token)
async def refresh_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).filter(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    token_data = {
        "sub": db_user.username,
        "email": db_user.email,
        "user_id": db_user.id
    }
    new_access_token = create_access_token(data=token_data)
    new_refresh_token = create_refresh_token(data=token_data)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

@router.get("/users/get", response_model=list[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    return await crud_users.get_all_users(db)


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:  # ← нельзя удалять чужой аккаунт
        raise HTTPException(status_code=403, detail="Not allowed")

    success = await crud_users.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

@router.get("/me", response_model=UserResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/tasks-count")
async def read_current_user_tasks_count(current_user: User = Depends(get_current_user)):
    return {"count": len(current_user.tasks)}

@router.get("/admin/panel")
def admin_panel(current_admin: User = Depends(get_current_admin)):
    return {"message": "Welcome to the admin panel!", "admin_name": current_admin.username}

@router.get("/users/{user_id}/tasks", response_model=UserWithTasksResponse)
async def get_user_with_tasks(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).options(joinedload(User.tasks)).filter(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

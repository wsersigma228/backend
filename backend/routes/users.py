from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from jose import jwt, ExpiredSignatureError, JWTError

from backend.config import SECRET_KEY, ALGORITHM
from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, UserResponse, UserLogin, Token, UserWithTasksResponse, TokenRefreshRequest
from backend.security import create_access_token, create_refresh_token, get_current_user, get_current_admin, verify_password, security
from backend.crud import users as crud_users

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    return crud_users.create_user(db=db, user_schemas=user)

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = crud_users.get_user_by_username(db, username=user.username)
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
def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    db_user = db.query(User).filter(User.id == user_id).first()
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
def get_users(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)  # ← добавили
):
    return crud_users.get_all_users(db)


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:  # нельзя удалять чужой аккаунт
        raise HTTPException(status_code=403, detail="Not allowed")

    success = crud_users.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me/tasks-count")
def read_current_user_tasks_count(current_user: User = Depends(get_current_user)):
    return {"count": len(current_user.tasks)}

@router.get("/admin/panel")
def admin_panel(current_admin: User = Depends(get_current_admin)):
    return {"message": "Welcome to the admin panel!", "admin_name": current_admin.username}


@router.get("/users/{user_id}/tasks", response_model=UserWithTasksResponse)
def get_user_with_tasks(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).options(joinedload(User.tasks)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

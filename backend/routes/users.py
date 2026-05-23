from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, ExpiredSignatureError, JWTError

from backend.config import SECRET_KEY, ALGORITHM
from backend.database import get_db
from backend.models import User
from backend.schemas import UserCreate, UserResponse, UserLogin, Token
from backend.security import create_access_token, get_current_user, verify_password, security
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

    access_token = create_access_token(data={
        "sub": db_user.username,
        "email": db_user.email,
        "user_id": db_user.id
    })
    return {"access_token": access_token, "token_type": "bearer"}

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
    if current_user.id != user_id:  # ← нельзя удалять чужой аккаунт
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

@router.get("/debug/token")
def debug_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

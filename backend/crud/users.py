from sqlalchemy.orm import Session
from backend.models import User
from backend.schemas import UserCreate
from backend.security import get_password_hash

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_all_users(db: Session):
    return db.query(User).all()

def create_user(db: Session, user_schemas: UserCreate):
    hashed_password = get_password_hash(user_schemas.password)
    new_user = User(
        username=user_schemas.username,
        email=user_schemas.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False
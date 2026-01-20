from sqlalchemy.orm import Session
from uuid import UUID
from fastapi import HTTPException

from app.models.user import User

def get_my_profile(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def get_all_users(db: Session):
    return db.query(User).all()


def deactivate_user(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is already deactivated")

    user.is_active = False
    db.commit()

    return {"message": "User deactivated"}


def activate_user(db: Session, user_id: UUID):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_active:
        raise HTTPException(status_code=400, detail="User is already active")

    user.is_active = True
    db.commit()

    return {"message": "User activated"}


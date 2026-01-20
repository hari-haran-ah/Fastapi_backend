from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.schemas.user import UserOut
from app.dependencies.auth import user_required, admin_required
from app.services.user_service import (
    get_my_profile,
    get_all_users,
    deactivate_user,
    activate_user
)

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
def read_me(
    current_user=Depends(user_required),
    db: Session = Depends(get_db)
):
    return get_my_profile(db, current_user["sub"])

@router.get("/all", response_model=list[UserOut])
def read_all_users(
    current_user=Depends(admin_required),
    db: Session = Depends(get_db)
):
    return get_all_users(db)

@router.patch("/deactivate/{user_id}")
def deactivate_user_api(
    user_id: UUID,
    current_user=Depends(admin_required),
    db: Session = Depends(get_db)
):
    return deactivate_user(db, user_id)

@router.patch("/activate/{user_id}")
def activate_user_api(
    user_id: UUID,
    current_user=Depends(admin_required),
    db: Session = Depends(get_db)
):
    return activate_user(db, user_id)

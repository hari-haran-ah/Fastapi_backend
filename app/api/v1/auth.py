from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate
from app.schemas.auth import LoginSchema, OTPSchema
from app.models.user import User
from app.services.auth_service import signup, verify_otp, login ,logout_user, logout_all_sessions
from app.utils.password import verify_password
from app.core.config import settings
from app.dependencies.auth import get_current_user  
from sqlalchemy import select
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup_api(data: UserCreate, db: Session = Depends(get_db)):
    return signup(db, data)

@router.post("/verify-otp")
def verify_otp_api(data: OTPSchema, db: Session = Depends(get_db)):
    return verify_otp(db, data.email, data.otp)

@router.post("/login")
async def login_api(
    data: LoginSchema,
    response: Response,
    db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.email == data.email)
    ).scalar_one_or_none()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Your account was deactivated. Please contact admin."
        )

    access_token, refresh_token = login(db, user)

    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE
    )

    return {"message": "Login successful"}

@router.post("/logout")
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    return logout_user(request, response, db)

@router.post("/logout-all-sessions")
def logout_all_sessions_api(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user["sub"]

    return logout_all_sessions(
        request=request,
        response=response,
        db=db,
        user_id=user_id
    )
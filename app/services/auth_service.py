from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, Response
from datetime import datetime, timedelta

from sqlalchemy import select

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.otp import OTP
from app.utils.password import hash_password, verify_password
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings
from app.services.email_service import EmailService
from app.services.otp_service import generate_otp, otp_expiry


def signup(db: Session, data):
    result = db.execute(
        select(User).where(User.email == data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    
    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password=hash_password(data.password),
        is_verified=False
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    
    otp_code = generate_otp()

    otp = OTP(
        email=user.email,
        otp=otp_code,
        expires_at=otp_expiry()
    )

    db.add(otp)
    db.commit()

    
    EmailService().send_otp_email(user.email, otp_code)

    return {"message": "Signup successful. Verify OTP."}

def verify_otp(db: Session, email: str, otp_code: str):
    otp = db.execute(
        select(OTP).where(OTP.email == email, OTP.otp == otp_code)
    ).scalar_one_or_none()

    if not otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    user =   db.execute(
        select(User).where(User.email == email)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_verified = True

    db.delete(otp)
    db.commit()

    return {"message": "Email verified successfully"}

def login(db: Session, user: User):
    if not verify_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    refresh_token = create_refresh_token({"sub": str(user.id)})

    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
    )

    db.add(db_token)
    db.commit()

    return access_token, refresh_token



def logout_user(request: Request, response: Response, db: Session):
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if refresh_token:
        db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).delete()
        db.commit()
    

    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        path="/"
    )
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path="/"
    )
    return {"message": "Logout successful"}

    
def logout_all_sessions(
    request: Request,
    response: Response,
    db: Session,
    user_id: str
):
    # 1️⃣ Delete ALL refresh tokens of this user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id
    ).delete(synchronize_session=False)

    db.commit()

    # 2️⃣ Delete cookies
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        path="/"
    )
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        path="/"
    )

    return {"message": "Logged out from all devices"}
    
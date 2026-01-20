from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.config import settings
from app.core.database import get_db
from app.models.refresh_token import RefreshToken
from app.core.security import create_access_token


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    access_token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)

    if access_token:
        try:
            payload = jwt.decode(
                access_token,
                settings.ACCESS_TOKEN_SECRET_KEY,
                algorithms=[settings.ACCESS_TOKEN_ALGORITHM]
            )
            return payload
        except JWTError:
            pass

    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Session expired. Please login again."
        )

    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == refresh_token,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()

    if not db_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token. Please login again."
        )

    payload = jwt.decode(
        refresh_token,
        settings.REFRESH_TOKEN_SECRET_KEY,
        algorithms=[settings.REFRESH_TOKEN_ALGORITHM]
    )

    new_access = create_access_token({
        "sub": payload["sub"],
        "role": payload.get("role", "user")
    })

    request.state.new_access_token = new_access
    return payload

def user_required(current_user=Depends(get_current_user)):
    return current_user

def admin_required(current_user=Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
    

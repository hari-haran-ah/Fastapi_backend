from fastapi import APIRouter, Request, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.oauth import oauth
from app.core.database import get_db
from app.models.user import User, Role
from app.models.refresh_token import RefreshToken
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter(prefix="/oauth", tags=["OAuth"])

@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)
    user_info = token["userinfo"]

    email = user_info["email"]
    name = user_info.get("name", "Google User")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        user = User(
            name=name,
            email=email,
            phone="",
            password="oauth",
            role=Role.USER,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(403, "Account deactivated")

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    refresh_token = create_refresh_token({"sub": str(user.id)})

    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(
                minutes=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )
    )
    db.commit()

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return {"message": "Google login successful"}


@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    token = await oauth.github.authorize_access_token(request)

    profile_resp = await oauth.github.get("user", token=token)
    profile = profile_resp.json()

    emails_resp = await oauth.github.get("user/emails", token=token)
    emails = emails_resp.json()

    primary_email = None
    for e in emails:
        if e.get("primary") and e.get("verified"):
            primary_email = e["email"]
            break

    if not primary_email:
        raise HTTPException(400, "GitHub email not available")

    name = profile.get("name") or profile.get("login")

    user = db.query(User).filter(User.email == primary_email).first()

    if not user:
        user = User(
            name=name,
            email=primary_email,
            phone=None,
            password="oauth",
            role=Role.user,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(403, "Account deactivated")

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })

    refresh_token = create_refresh_token({"sub": str(user.id)})

    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        )
    )
    db.commit()

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "GitHub login successful"}

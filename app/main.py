from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from app.core.database import engine, Base
from app.api.v1 import auth, oauth, users
from app.core.config import settings
from app.middlewares.token_refresh import token_refresh_middleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="oauth_session",
    same_site="lax",
    https_only=False
)


app.middleware("http")(token_refresh_middleware)


app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(oauth.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {"message": "Auth service running", "status": "ok"}

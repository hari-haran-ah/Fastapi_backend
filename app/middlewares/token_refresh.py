from fastapi import Request, Response
from app.core.config import settings

OAUTH_PATH_PREFIX = "/api/v1/oauth"

async def token_refresh_middleware(request: Request, call_next):
    """
    If a new access token is generated during request,
    attach it to the response cookies.
    """
    if request.url.path.startswith(OAUTH_PATH_PREFIX):
        return await call_next(request)
    response: Response = await call_next(request)

    if hasattr(request.state, "new_access_token"):
        response.set_cookie(
            key=settings.ACCESS_TOKEN_COOKIE_NAME,
            value=request.state.new_access_token,
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE
        )

    return response

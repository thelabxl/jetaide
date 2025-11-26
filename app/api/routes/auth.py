from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import settings
from app.core.oauth import oauth
from app.core.security import create_access_token
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/login")
async def google_login(request: Request):
    redirect_uri = f"{settings.backend_url}/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Google")

    # Find or create user
    result = await db.execute(
        select(User).where(User.oauth_provider == "google", User.oauth_id == user_info["sub"])
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=user_info["email"],
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            oauth_provider="google",
            oauth_id=user_info["sub"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})
    return RedirectResponse(url=f"{settings.frontend_url}?token={access_token}")


@router.get("/facebook/login")
async def facebook_login(request: Request):
    redirect_uri = f"{settings.backend_url}/auth/facebook/callback"
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


@router.get("/facebook/callback")
async def facebook_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await oauth.facebook.authorize_access_token(request)

    # Get user info from Facebook Graph API
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://graph.facebook.com/me",
            params={"fields": "id,name,email,picture", "access_token": token["access_token"]},
        )
        user_info = resp.json()

    if "error" in user_info:
        raise HTTPException(status_code=400, detail="Failed to get user info from Facebook")

    # Find or create user
    result = await db.execute(
        select(User).where(User.oauth_provider == "facebook", User.oauth_id == user_info["id"])
    )
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            email=user_info.get("email", f"{user_info['id']}@facebook.com"),
            name=user_info.get("name"),
            picture=user_info.get("picture", {}).get("data", {}).get("url"),
            oauth_provider="facebook",
            oauth_id=user_info["id"],
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(data={"sub": user.id})
    return RedirectResponse(url=f"{settings.frontend_url}?token={access_token}")


@router.get("/me")
async def get_me(request: Request, db: AsyncSession = Depends(get_db)):
    from app.api.deps import get_current_user
    from fastapi.security import HTTPAuthorizationCredentials

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing authorization header")

    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=auth_header[7:])
    user = await get_current_user(credentials, db)
    return {"id": user.id, "email": user.email, "name": user.name, "picture": user.picture}

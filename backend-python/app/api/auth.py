"""Auth endpoints: register, login, refresh, logout."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import CurrentUser, DbSession
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    token_response,
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register")
async def register(
    body: RegisterRequest,
    session: DbSession,
) -> dict:
    access_token, refresh_token, user = await auth_service.register(
        session,
        email=body.email,
        password=body.password,
        name=body.name,
    )
    return token_response(access_token, refresh_token, user)


@router.post("/login")
async def login(
    body: LoginRequest,
    session: DbSession,
) -> dict:
    access_token, refresh_token, user = await auth_service.login(
        session,
        email=body.email,
        password=body.password,
    )
    return token_response(access_token, refresh_token, user)


@router.post("/refresh")
async def refresh(
    body: RefreshRequest,
    session: DbSession,
) -> dict:
    access_token, refresh_token, user = await auth_service.refresh(
        session,
        refresh_token=body.refreshToken,
    )
    return token_response(access_token, refresh_token, user)


@router.post("/logout")
async def logout(
    body: LogoutRequest,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    await auth_service.logout(session, refresh_token=body.refreshToken)

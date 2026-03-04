"""Auth service: register, login, refresh, logout."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.repositories.refresh_token_repo import refresh_token_repo
from app.repositories.user_repo import user_repo
from app.schemas.user import UserResponse


def _user_response(user: User) -> UserResponse:
    return UserResponse(id=user.id, email=user.email, name=user.name)


async def register(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    name: str | None = None,
) -> tuple[str, str, UserResponse]:
    """Register user. Returns (access_token, refresh_token, user). Raises ConflictError if email exists."""
    existing = await user_repo.get_by_email(session, email)
    if existing:
        raise ConflictError("Email already registered", {"email": email})
    password_hash = hash_password(password)
    user = await user_repo.create(
        session, email=email, password_hash=password_hash, name=name
    )
    access_token = create_access_token(user.id, user.email)
    raw_refresh, expires_at = create_refresh_token(user.id)
    token_hash = hash_refresh_token(raw_refresh)
    await refresh_token_repo.create(
        session, user_id=user.id, token_hash=token_hash, expires_at=expires_at
    )
    return access_token, raw_refresh, _user_response(user)


async def login(
    session: AsyncSession,
    *,
    email: str,
    password: str,
) -> tuple[str, str, UserResponse]:
    """Login. Returns (access_token, refresh_token, user). Raises UnauthorizedError if invalid."""
    user = await user_repo.get_by_email(session, email)
    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    access_token = create_access_token(user.id, user.email)
    raw_refresh, expires_at = create_refresh_token(user.id)
    token_hash = hash_refresh_token(raw_refresh)
    await refresh_token_repo.create(
        session, user_id=user.id, token_hash=token_hash, expires_at=expires_at
    )
    return access_token, raw_refresh, _user_response(user)


async def refresh(
    session: AsyncSession,
    *,
    refresh_token: str,
) -> tuple[str, str, UserResponse]:
    """Validate refresh token, rotate (invalidate old), return new access + refresh + user."""
    token_hash = hash_refresh_token(refresh_token)
    # Find by hash only (we don't know user_id from opaque token)
    rt = await refresh_token_repo.get_by_hash(session, token_hash)
    if not rt or rt.revoked:
        raise UnauthorizedError("Invalid or expired refresh token")
    if rt.expires_at.tzinfo is None:
        rt.expires_at = rt.expires_at.replace(tzinfo=UTC)
    if rt.expires_at <= datetime.now(UTC):
        raise UnauthorizedError("Refresh token expired")
    user = await user_repo.get_by_id(session, rt.user_id)
    if not user:
        raise UnauthorizedError("User not found")
    # Rotate: revoke old
    await refresh_token_repo.revoke(session, rt)
    # Issue new
    access_token = create_access_token(user.id, user.email)
    raw_refresh, expires_at = create_refresh_token(user.id)
    new_hash = hash_refresh_token(raw_refresh)
    await refresh_token_repo.create(
        session, user_id=user.id, token_hash=new_hash, expires_at=expires_at
    )
    return access_token, raw_refresh, _user_response(user)


async def logout(session: AsyncSession, *, refresh_token: str) -> None:
    """Revoke the given refresh token."""
    token_hash = hash_refresh_token(refresh_token)
    rt = await refresh_token_repo.get_by_hash(session, token_hash)
    if rt and not rt.revoked:
        await refresh_token_repo.revoke(session, rt)

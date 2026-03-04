"""FastAPI dependencies: settings, DB session, current user."""

from uuid import UUID
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repo import user_repo

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    session: DbSession,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Validate Bearer token and return user entity. Raises UnauthorizedError if invalid."""
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError("Missing token")
    try:
        payload = decode_access_token(token)
    except Exception:
        raise UnauthorizedError("Invalid or expired token")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token payload")
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid token payload")
    user = await user_repo.get_by_id(session, user_id)
    if not user:
        raise UnauthorizedError("User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

"""Refresh token repository (store hashed tokens only)."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepo:
    async def create(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        rt = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        session.add(rt)
        await session.flush()
        await session.refresh(rt)
        return rt

    async def find_valid(
        self,
        session: AsyncSession,
        user_id: UUID,
        token_hash: str,
    ) -> RefreshToken | None:
        now = datetime.now(UTC)
        result = await session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_hash(
        self,
        session: AsyncSession,
        token_hash: str,
    ) -> RefreshToken | None:
        result = await session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def revoke(self, session: AsyncSession, token: RefreshToken) -> None:
        token.revoked = True
        await session.flush()


refresh_token_repo = RefreshTokenRepo()

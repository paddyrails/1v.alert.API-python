"""AlertDef repository. DB column 'title' maps to API 'name'."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alertdef import AlertDef


class AlertDefRepo:
    async def get_by_id(self, session: AsyncSession, alert_id: UUID) -> AlertDef | None:
        result = await session.execute(select(AlertDef).where(AlertDef.id == alert_id))
        return result.scalar_one_or_none()

    async def get_by_id_and_user(
        self, session: AsyncSession, alert_id: UUID, user_id: UUID
    ) -> AlertDef | None:
        result = await session.execute(
            select(AlertDef).where(AlertDef.id == alert_id, AlertDef.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        *,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[AlertDef], int]:
        offset = (page - 1) * limit
        count_result = await session.execute(
            select(func.count()).select_from(AlertDef).where(AlertDef.user_id == user_id)
        )
        total = count_result.scalar() or 0
        result = await session.execute(
            select(AlertDef)
            .where(AlertDef.user_id == user_id)
            .order_by(AlertDef.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        items = list(result.scalars().all())
        return items, total

    async def create(
        self,
        session: AsyncSession,
        *,
        user_id: UUID,
        title: str,
        description: str | None = None,
    ) -> AlertDef:
        alert = AlertDef(user_id=user_id, title=title, description=description)
        session.add(alert)
        await session.flush()
        await session.refresh(alert)
        return alert

    async def update(
        self,
        session: AsyncSession,
        alert: AlertDef,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> AlertDef:
        if title is not None:
            alert.title = title
        if description is not None:
            alert.description = description
        await session.flush()
        await session.refresh(alert)
        return alert

    async def delete(self, session: AsyncSession, alert: AlertDef) -> None:
        await session.delete(alert)
        await session.flush()


alertdef_repo = AlertDefRepo()

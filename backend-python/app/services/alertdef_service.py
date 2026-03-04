"""AlertDef service. Maps API 'name' to DB 'title'."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.alertdef import AlertDef
from app.models.user import User
from app.repositories.alertdef_repo import alertdef_repo
from app.schemas.alertdef import alertdef_to_response


async def list_alertdefs(
    session: AsyncSession,
    user: User,
    *,
    page: int = 1,
    limit: int = 20,
) -> tuple[list[dict], int]:
    """Return (items as response dicts, total)."""
    items, total = await alertdef_repo.list_for_user(
        session, user.id, page=page, limit=limit
    )
    out = [
        alertdef_to_response(
            id=a.id,
            name=a.title,
            description=a.description,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )
        for a in items
    ]
    return out, total


async def get_alertdef(
    session: AsyncSession,
    user: User,
    alert_id: UUID,
) -> dict:
    alert = await alertdef_repo.get_by_id_and_user(session, alert_id, user.id)
    if not alert:
        raise NotFoundError("AlertDef", str(alert_id))
    return alertdef_to_response(
        id=alert.id,
        name=alert.title,
        description=alert.description,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
    )


async def create_alertdef(
    session: AsyncSession,
    user: User,
    *,
    name: str,
    description: str | None = None,
) -> dict:
    alert = await alertdef_repo.create(
        session, user_id=user.id, title=name, description=description
    )
    return alertdef_to_response(
        id=alert.id,
        name=alert.title,
        description=alert.description,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
    )


async def update_alertdef(
    session: AsyncSession,
    user: User,
    alert_id: UUID,
    *,
    name: str | None = None,
    description: str | None = None,
) -> dict:
    alert = await alertdef_repo.get_by_id_and_user(session, alert_id, user.id)
    if not alert:
        raise NotFoundError("AlertDef", str(alert_id))
    await alertdef_repo.update(
        session, alert, title=name, description=description
    )
    return alertdef_to_response(
        id=alert.id,
        name=alert.title,
        description=alert.description,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
    )


async def delete_alertdef(
    session: AsyncSession,
    user: User,
    alert_id: UUID,
) -> None:
    alert = await alertdef_repo.get_by_id_and_user(session, alert_id, user.id)
    if not alert:
        raise NotFoundError("AlertDef", str(alert_id))
    await alertdef_repo.delete(session, alert)

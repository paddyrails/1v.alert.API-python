"""AlertDef CRUD endpoints (protected)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.deps import CurrentUser, DbSession
from app.schemas.alertdef import AlertDefCreate, AlertDefUpdate
from app.services import alertdef_service

router = APIRouter(prefix="/api/alertdefs", tags=["alertdefs"])


@router.post("")
async def create_alertdef(
    body: AlertDefCreate,
    session: DbSession,
    current_user: CurrentUser,
) -> dict:
    return await alertdef_service.create_alertdef(
        session,
        current_user,
        name=body.name,
        description=body.description,
    )


@router.get("")
async def list_alertdefs(
    session: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    items, total = await alertdef_service.list_alertdefs(
        session, current_user, page=page, limit=limit
    )
    return {"items": items, "page": page, "limit": limit, "total": total}


@router.get("/{id}")
async def get_alertdef(
    id: UUID,
    session: DbSession,
    current_user: CurrentUser,
) -> dict:
    return await alertdef_service.get_alertdef(session, current_user, id)


@router.patch("/{id}")
async def update_alertdef(
    id: UUID,
    body: AlertDefUpdate,
    session: DbSession,
    current_user: CurrentUser,
) -> dict:
    return await alertdef_service.update_alertdef(
        session,
        current_user,
        id,
        name=body.name,
        description=body.description,
    )


@router.delete("/{id}", status_code=204)
async def delete_alertdef(
    id: UUID,
    session: DbSession,
    current_user: CurrentUser,
) -> None:
    await alertdef_service.delete_alertdef(session, current_user, id)

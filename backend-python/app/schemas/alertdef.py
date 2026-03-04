"""AlertDef schemas. API uses 'name', DB uses 'title'."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AlertDefCreate(BaseModel):
    name: str = Field(..., min_length=1)
    description: str | None = None


class AlertDefUpdate(BaseModel):
    name: str | None = Field(None, min_length=1)
    description: str | None = None


class AlertDefResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    createdAt: datetime = Field(..., alias="createdAt")
    updatedAt: datetime = Field(..., alias="updatedAt")

    model_config = {"populate_by_name": True}


def alertdef_to_response(
    id: UUID,
    name: str,
    description: str | None,
    created_at: datetime,
    updated_at: datetime,
) -> dict:
    return {
        "id": id,
        "name": name,
        "description": description,
        "createdAt": created_at.isoformat(),
        "updatedAt": updated_at.isoformat(),
    }

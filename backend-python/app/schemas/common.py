"""Common schemas (pagination, etc.)."""

from pydantic import BaseModel, Field


class PaginatedMeta(BaseModel):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)

"""AlertDef tests: create without token -> 401, with token -> success."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_alertdef_without_token_returns_401(client: AsyncClient) -> None:
    r = await client.post(
        "/api/alertdefs",
        json={"name": "My Alert", "description": "Test"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_alertdef_with_token_success(client: AsyncClient) -> None:
    # Register and get token
    r = await client.post(
        "/api/auth/register",
        json={"email": "alertdef@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    access = r.json()["accessToken"]

    # Create alertdef
    r2 = await client.post(
        "/api/alertdefs",
        json={"name": "My Alert", "description": "Test"},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200
    data = r2.json()
    assert data["name"] == "My Alert"
    assert data["description"] == "Test"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data

    # List
    r3 = await client.get(
        "/api/alertdefs",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r3.status_code == 200
    assert r3.json()["total"] >= 1
    assert len(r3.json()["items"]) >= 1

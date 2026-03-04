"""Auth tests: register, login, refresh, logout."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_returns_tokens(client: AsyncClient) -> None:
    # Register
    r = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123", "name": "Test"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "accessToken" in data
    assert "refreshToken" in data
    assert data.get("tokenType") == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test"

    # Login
    r2 = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert r2.status_code == 200
    data2 = r2.json()
    assert "accessToken" in data2
    assert "refreshToken" in data2


@pytest.mark.asyncio
async def test_refresh_rotates_token(client: AsyncClient) -> None:
    # Register and get refresh token
    r = await client.post(
        "/api/auth/register",
        json={"email": "refresh@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    old_refresh = r.json()["refreshToken"]
    access = r.json()["accessToken"]

    # Refresh
    r2 = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": old_refresh},
    )
    assert r2.status_code == 200
    new_refresh = r2.json()["refreshToken"]
    assert new_refresh != old_refresh

    # Old refresh token is invalidated
    r3 = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": old_refresh},
    )
    assert r3.status_code == 401


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client: AsyncClient) -> None:
    r = await client.post(
        "/api/auth/register",
        json={"email": "logout@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    refresh = r.json()["refreshToken"]
    access = r.json()["accessToken"]

    # Logout (revoke refresh token)
    r2 = await client.post(
        "/api/auth/logout",
        json={"refreshToken": refresh},
        headers={"Authorization": f"Bearer {access}"},
    )
    assert r2.status_code == 200

    # Refresh with revoked token fails
    r3 = await client.post(
        "/api/auth/refresh",
        json={"refreshToken": refresh},
    )
    assert r3.status_code == 401

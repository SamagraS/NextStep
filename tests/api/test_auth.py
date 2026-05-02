import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
async def test_auth_login(client: AsyncClient):
    payload = {"email": "manager@nextstep.com", "password": "pmpass"}
    response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["role"] == "portfolio_manager"
    assert data["full_name"] == "Portfolio Lead"
    assert data["access_token"]


@pytest.mark.api
@pytest.mark.asyncio
async def test_auth_login_rejects_invalid_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "manager@nextstep.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.asyncio
async def test_auth_login_rejects_unknown_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": "pmpass"},
    )

    assert response.status_code == 401

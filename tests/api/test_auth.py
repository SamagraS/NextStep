import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.asyncio
async def test_auth_login(client: AsyncClient):
    payload = {
        "email": "manager@nextstep.com",
        "password": "pmpass"
    }
    # This endpoint is currently a gap identified in the audit
    # But we write the test for TDD.
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/health", "/api/v1/health"])
async def test_health_check(client: AsyncClient, path: str):
    response = await client.get(path)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert data["database"]["status"] == "ok"
    assert isinstance(data["artifacts"], list)

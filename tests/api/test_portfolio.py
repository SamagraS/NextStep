import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.asyncio
async def test_portfolio_dashboard(client: AsyncClient):
    response = await client.get("/api/v1/portfolio/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "cohorts" in data
    assert "latest_alerts" in data
    assert "amber_count" in data

@pytest.mark.api
@pytest.mark.asyncio
async def test_portfolio_rescore(client: AsyncClient):
    response = await client.post("/api/v1/portfolio/rescore")
    assert response.status_code == 202

import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
async def test_portfolio_dashboard(client: AsyncClient):
    response = await client.get("/api/v1/portfolio/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_active_cohorts"] > 0
    assert "cohorts" in data
    assert "latest_alerts" in data
    assert "amber_count" in data
    assert "red_count" in data


@pytest.mark.api
@pytest.mark.asyncio
async def test_portfolio_cohorts(client: AsyncClient):
    response = await client.get("/api/v1/portfolio/cohorts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(row["cohort_id"] == "cohort-us-cs" for row in data)


@pytest.mark.api
@pytest.mark.asyncio
async def test_portfolio_alerts(client: AsyncClient):
    response = await client.get("/api/v1/portfolio/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(alert["severity"] in {"AMBER", "RED"} for alert in data)


@pytest.mark.api
@pytest.mark.asyncio
async def test_portfolio_rescore(client: AsyncClient):
    response = await client.post("/api/v1/portfolio/rescore")
    assert response.status_code == 202

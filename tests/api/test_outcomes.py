import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
async def test_outcomes_prediction(client: AsyncClient):
    payload = {
        "program_family": "computer science",
        "destination_country": "United States",
        "institution_tier": 1,
    }

    response = await client.post("/api/v1/outcomes/predict", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["student_context"]["program_family"] == "computer_science"
    assert data["student_context"]["country"] == "United States"
    assert data["student_context"]["institution_tier"] == 1
    assert data["placement_probabilities"]["p_3_months"] >= 0
    assert data["salary_band"]["p50"] >= 0
    assert data["risk_score"]["label"] in {"low", "medium", "high"}
    assert data["sources_used"]
    assert isinstance(data["notes"], list)
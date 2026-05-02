import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.asyncio
async def test_score_origination(client: AsyncClient):
    payload = {
        "student_id": "STU-001",
        "full_name": "John Doe",
        "university_name": "Stanford University",
        "program_name": "Computer Science",
        "destination_country": "USA",
        "target_sector": "Technology",
        "cgpa": 9.0,
        "cgpa_present": True,
        "internship_count": 2,
        "internship_count_present": True,
        "stem_opt_eligible": True,
        "stem_opt_eligible_present": True,
        "loan_amount_inr": 4000000,
        "interest_rate_annual_pct": 10.5,
        "repayment_term_months": 120,
        "moratorium_months": 24
    }
    response = await client.post("/api/v1/score/origination", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "application_id" in data
    assert "repayment_score" in data
    assert data["repayment_score"]["score"] > 0

@pytest.mark.api
@pytest.mark.asyncio
async def test_get_latest_score_not_found(client: AsyncClient):
    response = await client.get("/api/v1/score/NON_EXISTENT/latest")
    assert response.status_code == 404

@pytest.mark.skip(reason="Hangs test suite due to infinite stream")
@pytest.mark.api
@pytest.mark.asyncio
async def test_stream_score_updates(client: AsyncClient):
    # Just verify the endpoint accepts requests and returns a stream (or closes if no events immediately)
    async with client.stream("GET", "/api/v1/score/APP-TEST/stream") as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]

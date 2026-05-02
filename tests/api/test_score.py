import pytest
from httpx import AsyncClient

from app.main import app as main_app


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
        "moratorium_months": 24,
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


@pytest.mark.api
@pytest.mark.asyncio
async def test_stream_score_updates(client: AsyncClient, monkeypatch):
    async def fake_stream(request, application_id):
        yield "event: student_profile_updated\n"
        yield (
            'data: {"new_score":82,"prev_score":74,"delta":8,'
            '"tenacity_score":0.9,"behavioral_engagement":"HIGH"}\n\n'
        )

    monkeypatch.setattr(main_app.state.notifier, "stream", fake_stream)

    response = await client.get("/api/v1/score/fake-application/stream")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "student_profile_updated" in response.text
    assert "new_score" in response.text

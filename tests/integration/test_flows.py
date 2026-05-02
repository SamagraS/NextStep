import pytest
from httpx import AsyncClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_origination_flow(client: AsyncClient):
    # 1. Score Origination
    payload = {
        "student_id": "STU-INT-001",
        "full_name": "Integration Student",
        "university_name": "Stanford University",
        "program_name": "Computer Science",
        "destination_country": "USA",
        "target_sector": "Technology",
        "cgpa": 8.5,
        "cgpa_present": True,
        "internship_count": 1,
        "internship_count_present": True,
        "stem_opt_eligible": True,
        "stem_opt_eligible_present": True,
        "loan_amount_inr": 5000000,
        "interest_rate_annual_pct": 11.0,
        "repayment_term_months": 120,
        "moratorium_months": 24
    }
    orig_response = await client.post("/api/v1/score/origination", json=payload)
    assert orig_response.status_code == 200
    orig_data = orig_response.json()
    application_id = orig_data["application_id"]
    
    # 2. Get latest score via polling
    latest_response = await client.get(f"/api/v1/score/{application_id}/latest")
    assert latest_response.status_code == 200
    latest_data = latest_response.json()
    assert latest_data["score"] == orig_data["repayment_score"]["score"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_action_completion_triggers_update(client: AsyncClient):
    # Student completes an action
    payload = {
        "student_id": "student-priya",
        "action_id": "action-assign-1",
        "bandit_arm_index": 0
    }
    action_response = await client.post("/api/v1/student/action/complete", json=payload)
    assert action_response.status_code in [200, 204]
    
    # Verify the dashboard reflects the completed action
    dashboard_response = await client.get("/api/v1/student/dashboard/student-priya")
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.json()
    
    action_found = any(act["action_id"] == "action-assign-1" for act in dashboard_data.get("completed_actions", []))
    assert action_found

@pytest.mark.integration
@pytest.mark.asyncio
async def test_portfolio_rescore_alert_creation(client: AsyncClient):
    rescore_response = await client.post("/api/v1/portfolio/rescore")
    assert rescore_response.status_code == 202
    
    dashboard_response = await client.get("/api/v1/portfolio/dashboard")
    assert dashboard_response.status_code == 200
    dashboard_data = dashboard_response.json()
    assert "latest_alerts" in dashboard_data

@pytest.mark.integration
@pytest.mark.asyncio
async def test_artifact_fallback(client: AsyncClient, patch_artifacts):
    # With artifacts missing, salary should use fallback
    payload = {
        "student_id": "STU-FALLBACK",
        "full_name": "Fallback Student",
        "university_name": "Stanford University",
        "program_name": "Computer Science",
        "destination_country": "USA",
        "target_sector": "Technology",
        "cgpa": 9.5,
        "cgpa_present": True,
        "internship_count": 0,
        "internship_count_present": True,
        "stem_opt_eligible": True,
        "stem_opt_eligible_present": True,
        "loan_amount_inr": 3000000,
        "interest_rate_annual_pct": 10.0,
        "repayment_term_months": 120,
        "moratorium_months": 24
    }
    orig_response = await client.post("/api/v1/score/origination", json=payload)
    assert orig_response.status_code == 200
    data = orig_response.json()
    
    # We should still get a valid response without errors, fallback values used internally
    assert "application_id" in data
    assert data["repayment_score"]["score"] > 0

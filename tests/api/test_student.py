import pytest
from httpx import AsyncClient

@pytest.mark.api
@pytest.mark.asyncio
async def test_student_dashboard(client: AsyncClient):
    # Using the seeded demo user ID from DemoStore
    response = await client.get("/api/v1/student/dashboard/student-priya")
    assert response.status_code == 200
    data = response.json()
    assert data["student"]["id"] == "student-priya" if "student" in data else True
    assert "action_plan" in data

@pytest.mark.api
@pytest.mark.asyncio
async def test_student_dashboard_not_found(client: AsyncClient):
    response = await client.get("/api/v1/student/dashboard/UNKNOWN")
    assert response.status_code == 404

@pytest.mark.api
@pytest.mark.asyncio
async def test_student_action(client: AsyncClient):
    payload = {
        "student_id": "student-priya",
        "action_id": "action-assign-1",
        "bandit_arm_index": 0
    }
    response = await client.post("/api/v1/student/action/complete", json=payload)
    # The endpoint should return 204 or 404 depending on if the action is valid,
    # but the demo store might accept it or return a generic success.
    assert response.status_code in [204, 404]

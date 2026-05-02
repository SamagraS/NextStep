def test_origination_scoring_sync(test_app):
    payload = {
        "full_name": "Test Student",
        "university_name": "Stanford University",
        "program_name": "MS Computer Science",
        "destination_country": "United States",
        "target_sector": "Tech",
        "loan_amount_inr": 5000000,
        "interest_rate_annual_pct": 10.5,
        "repayment_term_months": 120,
        "moratorium_months": 6
    }
    response = test_app.post("/api/v1/score/origination", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "application_id" in data
    assert "repayment_score" in data
    assert "explanation" in data
    assert "salary_forecast" in data
    assert len(data["next_best_action"]) > 0

def test_latest_score_polling(test_app):
    # First create an application
    payload = {
        "full_name": "Priya Sharma",
        "university_name": "Stanford University",
        "program_name": "MS Computer Science",
        "destination_country": "United States",
        "target_sector": "Tech",
        "loan_amount_inr": 5000000,
        "interest_rate_annual_pct": 10.5,
        "repayment_term_months": 120,
        "moratorium_months": 6
    }
    resp1 = test_app.post("/api/v1/score/origination", json=payload)
    app_id = resp1.json()["application_id"]
    
    # Then poll for latest
    resp2 = test_app.get(f"/api/v1/score/{app_id}/latest")
    assert resp2.status_code == 200
    data = resp2.json()
    assert "score" in data
    assert "tier" in data

def test_portfolio_dashboard(test_app):
    response = test_app.get("/api/v1/portfolio/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "cohorts" in data
    assert "latest_alerts" in data
    assert data["total_active_cohorts"] > 0

def test_portfolio_rescore_durability(test_app):
    # 1. Trigger rescore
    resp_rescore = test_app.post("/api/v1/portfolio/rescore")
    assert resp_rescore.status_code == 202
    
    # 2. Verify alert exists
    resp_alerts = test_app.get("/api/v1/portfolio/alerts")
    assert resp_alerts.status_code == 200
    alerts = resp_alerts.json()
    assert any(a["severity"] == "AMBER" for a in alerts)

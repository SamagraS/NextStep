def test_health_endpoint(test_app):
    response = test_app.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "artifacts" in data
    assert data["database"]["status"] == "ok"

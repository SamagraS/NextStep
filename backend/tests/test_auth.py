def test_auth_login_success(test_app):
    payload = {
        "email": "priya@example.com",
        "password": "password123"
    }
    response = test_app.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "student"
    assert data["full_name"] == "Priya Sharma"

def test_auth_login_aravind_success(test_app):
    payload = {
        "email": "aravind@example.com",
        "password": "password123"
    }
    response = test_app.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Aravind Nair"

def test_auth_login_invalid_password(test_app):
    payload = {
        "email": "priya@example.com",
        "password": "wrongpassword"
    }
    response = test_app.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

def test_auth_login_non_existent_user(test_app):
    payload = {
        "email": "nobody@example.com",
        "password": "password123"
    }
    response = test_app.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401

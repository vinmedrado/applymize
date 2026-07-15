def test_register_login_refresh_me(client):
    payload = {
        "tenant_name": "Acme",
        "full_name": "Vinicius",
        "email": "vinicius@test.com",
        "password": "Strong123!",
        "skills": "Python, SQL",
        "seniority": "mid",
        "target_role": "Data Analyst",
    }
    register = client.post("/api/auth/register", json=payload)
    assert register.status_code == 200
    assert "access_token" in register.json()
    assert "refresh_token" in register.json()

    login = client.post("/api/auth/login", json={"email": "vinicius@test.com", "password": "Strong123!"})
    assert login.status_code == 200

    refresh = client.post("/api/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    assert refresh.status_code == 200

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {refresh.json()['access_token']}"})
    assert me.status_code == 200
    assert me.json()["tenant_name"] == "Acme"


def test_login_invalid_password(client):
    payload = {
        "tenant_name": "Acme",
        "full_name": "User",
        "email": "badlogin@test.com",
        "password": "Strong123!",
    }
    assert client.post("/api/auth/register", json=payload).status_code == 200
    login = client.post("/api/auth/login", json={"email": "badlogin@test.com", "password": "wrong"})
    assert login.status_code == 401


def test_weak_password_rejected(client):
    payload = {
        "tenant_name": "Acme",
        "full_name": "User",
        "email": "weak@test.com",
        "password": "123456",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_logout_revokes_refresh(client):
    payload = {
        "tenant_name": "Acme",
        "full_name": "User",
        "email": "logout@test.com",
        "password": "Strong123!",
    }
    register = client.post("/api/auth/register", json=payload)
    assert register.status_code == 200
    access = register.json()["access_token"]
    refresh = register.json()["refresh_token"]

    logout = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
        json={"refresh_token": refresh},
    )
    assert logout.status_code == 200

    revoked = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert revoked.status_code == 401


def test_invalid_refresh_token(client):
    response = client.post("/api/auth/refresh", json={"refresh_token": "invalid.token.value"})
    assert response.status_code == 401

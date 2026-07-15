def test_onboarding_default_false(client, auth_headers):
    response = client.get("/api/user/onboarding-status", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json() == {"completed": False}


def test_onboarding_complete(client, auth_headers):
    response = client.post("/api/user/onboarding-complete", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json() == {"completed": True}


def test_onboarding_read_after_complete(client, auth_headers):
    client.post("/api/user/onboarding-complete", headers=auth_headers)
    response = client.get("/api/user/onboarding-status", headers=auth_headers)
    assert response.status_code == 200, response.text
    assert response.json()["completed"] is True


def test_onboarding_requires_auth(client):
    response = client.get("/api/user/onboarding-status")
    assert response.status_code in {401, 403}

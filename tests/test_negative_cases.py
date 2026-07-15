def auth(client):
    response = client.post("/api/auth/register", json={
        "tenant_name": "Negative Tenant",
        "full_name": "Negative User",
        "email": "negative@test.com",
        "password": "Strong123!",
        "skills": "Python, SQL, FastAPI",
        "seniority": "mid",
        "target_role": "Backend Python",
    })
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}, response.json()


def test_invalid_login(client):
    client.post("/api/auth/register", json={
        "tenant_name": "Login Tenant",
        "full_name": "Login User",
        "email": "login@test.com",
        "password": "Strong123!",
        "skills": "Python",
        "seniority": "mid",
        "target_role": "Developer",
    })
    response = client.post("/api/auth/login", json={"email": "login@test.com", "password": "wrong"})
    assert response.status_code == 401


def test_invalid_refresh_token(client):
    response = client.post("/api/auth/refresh", json={"refresh_token": "invalid.token.value"})
    assert response.status_code == 401


def test_duplicate_application_returns_conflict(client):
    headers, _ = auth(client)
    job = client.post("/api/jobs/", headers=headers, json={
        "title": "Duplicate Application Job",
        "company": "DupCo",
        "description": "Python SQL FastAPI",
        "requirements": "Python, SQL",
        "source": "manual",
        "external_id": "dup-app-job",
    })
    assert job.status_code == 200
    job_id = job.json()["id"]

    first = client.post("/api/applications/", headers=headers, json={"job_id": job_id, "status": "applied"})
    assert first.status_code == 200
    second = client.post("/api/applications/", headers=headers, json={"job_id": job_id, "status": "applied"})
    assert second.status_code == 409


def test_duplicate_source_external_id_returns_conflict(client):
    headers, _ = auth(client)
    payload = {
        "title": "Duplicate Job",
        "company": "DupCo",
        "description": "Python SQL",
        "requirements": "Python",
        "source": "manual",
        "external_id": "same-external-id",
    }
    first = client.post("/api/jobs/", headers=headers, json=payload)
    assert first.status_code == 200, first.text
    second = client.post("/api/jobs/", headers=headers, json={**payload, "title": "Duplicate Job 2"})
    assert second.status_code == 409

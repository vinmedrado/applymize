def test_analytics_overview_endpoint(client, auth_headers):
    response = client.get("/api/analytics/overview", headers=auth_headers)
    assert response.status_code == 200
    assert "jobs_total" in response.json()


def test_skill_gap_endpoint_fallback(client, auth_headers):
    response = client.get("/api/skill-gap/roadmap", headers=auth_headers)
    assert response.status_code == 200
    assert "roadmap" in response.json()


def test_cover_letter_endpoint(client, auth_headers):
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Data Analyst",
        "company": "Tech",
        "description": "Python SQL Power BI",
        "requirements": "Python, SQL",
        "location": "Remote",
        "url": "https://example.com/cover",
        "source": "manual",
        "external_id": "cover-1",
        "remote": True,
    })
    assert job.status_code == 200
    response = client.get(f"/api/cover-letter/jobs/{job.json()['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert "short_message" in response.json()
    assert "application_email" in response.json()


def test_followup_endpoint(client, auth_headers):
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend Developer",
        "company": "Tech",
        "description": "Python FastAPI",
        "requirements": "Python, FastAPI",
        "location": "Remote",
        "url": "https://example.com/follow",
        "source": "manual",
        "external_id": "follow-1",
        "remote": True,
    })
    app = client.post("/api/applications/", headers=auth_headers, json={"job_id": job.json()["id"], "status": "applied"})
    assert app.status_code == 200
    response = client.get(f"/api/followups/{app.json()['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert "message" in response.json()


def test_radar_run_and_history(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.job_radar.ingest_jobs", lambda *a, **k: {"inserted": 0})
    response = client.post("/api/radar/run?provider=remoteok&limit=1", headers=auth_headers)
    assert response.status_code == 200
    assert "high_priority_count" in response.json()
    hist = client.get("/api/radar/history", headers=auth_headers)
    assert hist.status_code == 200
    assert isinstance(hist.json(), list)

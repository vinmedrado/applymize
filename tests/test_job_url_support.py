def test_job_with_url_returns_correctly(client, auth_headers):
    payload = {
        "title": "Data Engineer URL",
        "company": "URL Corp",
        "description": "Python SQL ETL",
        "requirements": "Python, SQL",
        "location": "Remote",
        "url": "https://remoteok.com/remote-jobs/test-url",
        "source": "manual",
        "external_id": "url-test-1",
        "seniority": "mid",
        "remote": True,
    }
    created = client.post("/api/jobs/", headers=auth_headers, json=payload)
    assert created.status_code == 200, created.text
    assert created.json()["url"] == payload["url"]

    fetched = client.get(f"/api/jobs/{created.json()['id']}", headers=auth_headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["url"] == payload["url"]

    listed = client.get("/api/jobs/", headers=auth_headers)
    assert listed.status_code == 200
    assert any(job["id"] == created.json()["id"] and job["url"] == payload["url"] for job in listed.json())


def test_job_without_url_does_not_break_api(client, auth_headers):
    created = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "No URL Job",
        "company": "No URL Corp",
        "description": "Python SQL",
        "requirements": "Python",
        "location": "",
        "url": "",
        "source": "manual",
        "external_id": "no-url-test-1",
        "seniority": "mid",
        "remote": False,
    })
    assert created.status_code == 200, created.text
    assert created.json()["url"] == ""

    fetched = client.get(f"/api/jobs/{created.json()['id']}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.json()["url"] == ""


def test_application_agent_returns_job_url(client, auth_headers):
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend FastAPI URL",
        "company": "Agent URL Corp",
        "description": "Python FastAPI PostgreSQL Docker APIs",
        "requirements": "Python, FastAPI, PostgreSQL, Docker",
        "location": "Remote",
        "url": "https://www.linkedin.com/jobs/view/applymize-agent-url",
        "source": "manual",
        "external_id": "agent-url-test-1",
        "seniority": "mid",
        "remote": True,
    })
    assert job.status_code == 200, job.text

    # Ensure profile is complete enough for the agent in setups that enforce completeness.
    client.put("/api/profile/me", headers=auth_headers, json={
        "full_name": "URL User",
        "professional_title": "Backend Python",
        "summary": "Python FastAPI PostgreSQL Docker APIs",
        "location": "Remote",
        "work_preferences": "remote",
        "salary_expectation": 8000,
        "phone": "11999999999",
        "email": "url@example.com",
    })
    client.post("/api/profile/skills", headers=auth_headers, json={"name": "Python", "level": "advanced", "category": "technical"})
    client.post("/api/profile/skills", headers=auth_headers, json={"name": "FastAPI", "level": "advanced", "category": "technical"})
    client.post("/api/profile/projects", headers=auth_headers, json={"name": "API Project", "description": "FastAPI PostgreSQL Docker", "technologies": "Python, FastAPI, Docker"})

    queue = client.post("/api/application-agent/build-queue", headers=auth_headers, json={
        "limit": 5,
        "min_strategy_score": 0,
        "generate_cv": True,
        "generate_message": True,
    })
    assert queue.status_code == 200, queue.text

    listed = client.get("/api/application-agent/queue", headers=auth_headers)
    assert listed.status_code == 200
    payload = listed.json()
    assert any(item["job_id"] == job.json()["id"] and item["job_url"] == "https://www.linkedin.com/jobs/view/applymize-agent-url" for item in payload)

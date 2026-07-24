def create_job(client, auth_headers, title, requirements, remote=True):
    response = client.post("/api/jobs/", headers=auth_headers, json={
        "title": title,
        "company": "Agent Test",
        "description": f"{title} Python SQL FastAPI Docker PostgreSQL APIs",
        "requirements": requirements,
        "seniority": "mid",
        "remote": remote,
        "location": "Remote" if remote else "São Paulo"
    })
    assert response.status_code == 200, response.text
    return response.json()


def test_build_queue_high_medium_only(client, auth_headers):
    create_job(client, auth_headers, "Backend FastAPI Developer", "Python, FastAPI, PostgreSQL, Docker", True)
    create_job(client, auth_headers, "Analista Dados SQL", "Python, SQL, Power BI", True)

    response = client.post("/api/application-agent/build-queue", headers=auth_headers, json={
        "limit": 5,
        "min_strategy_score": 58,
        "generate_cv": True,
        "generate_message": True
    })
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["created"] >= 1
    assert payload["items"]
    assert all(item["status"] == "queued" for item in payload["items"])
    assert all(item["evaluation_grade"] in ["A", "B", "C", "D"] for item in payload["items"])


def test_queue_does_not_duplicate(client, auth_headers):
    create_job(client, auth_headers, "Backend FastAPI Developer", "Python, FastAPI, PostgreSQL, Docker", True)

    first = client.post("/api/application-agent/build-queue", headers=auth_headers, json={"limit": 5})
    second = client.post("/api/application-agent/build-queue", headers=auth_headers, json={"limit": 5})
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["created"] == 0
    assert second.json()["skipped"] >= 1


def test_queue_blocks_low_priority(client, auth_headers):
    create_job(client, auth_headers, "Auxiliar Genérico", "Atendimento, Rotina administrativa", False)

    response = client.post("/api/application-agent/build-queue", headers=auth_headers, json={
        "limit": 5,
        "min_strategy_score": 95
    })
    assert response.status_code == 200
    assert response.json()["created"] == 0
    assert response.json()["blocked_low_priority"] >= 1


def test_approve_skip_mark_applied(client, auth_headers):
    create_job(client, auth_headers, "Backend FastAPI Developer", "Python, FastAPI, PostgreSQL, Docker", True)

    build = client.post("/api/application-agent/build-queue", headers=auth_headers, json={"limit": 5})
    assert build.status_code == 200, build.text
    item = build.json()["items"][0]
    queue_id = item["id"]

    approve = client.post(f"/api/application-agent/{queue_id}/approve", headers=auth_headers)
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    applied = client.post(f"/api/application-agent/{queue_id}/mark-applied", headers=auth_headers)
    assert applied.status_code == 200
    assert applied.json()["status"] == "applied"

    queue = client.get("/api/application-agent/queue", headers=auth_headers)
    assert queue.status_code == 200
    assert queue.json()[0]["status"] == "applied"


def test_skip(client, auth_headers):
    create_job(client, auth_headers, "Backend Python SQL", "Python, SQL, FastAPI", True)

    build = client.post("/api/application-agent/build-queue", headers=auth_headers, json={"limit": 5})
    assert build.status_code == 200
    queue_id = build.json()["items"][0]["id"]

    skipped = client.post(f"/api/application-agent/{queue_id}/skip", headers=auth_headers)
    assert skipped.status_code == 200
    assert skipped.json()["status"] == "skipped"

def test_job_crud_and_matching(client, auth_headers):
    create = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend Python Developer",
        "company": "Tech",
        "description": "Python FastAPI SQL Docker PostgreSQL APIs",
        "requirements": "Python, FastAPI, SQL, Docker",
        "seniority": "mid",
        "remote": True
    })
    assert create.status_code == 200, create.text
    job_id = create.json()["id"]

    listed = client.get("/api/jobs/", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    match = client.post(f"/api/matching/jobs/{job_id}", headers=auth_headers)
    assert match.status_code == 200
    assert match.json()["score"] > 50

    rank = client.post("/api/matching/rank", headers=auth_headers)
    assert rank.status_code == 200
    assert rank.json()[0]["job_id"] == job_id

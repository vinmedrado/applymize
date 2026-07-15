def test_application_cv_interview_flow(client, auth_headers):
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Analista de Dados",
        "company": "DataCo",
        "description": "Python SQL Power BI APIs automação ETL",
        "requirements": "Python, SQL, Power BI",
        "seniority": "mid",
        "remote": True
    })
    assert job.status_code == 200
    job_id = job.json()["id"]

    app = client.post("/api/applications/", headers=auth_headers, json={"job_id": job_id, "status": "applied", "notes": "Aplicado"})
    assert app.status_code == 200
    app_id = app.json()["id"]

    update = client.patch(f"/api/applications/{app_id}", headers=auth_headers, json={"status": "interview", "next_action": "Preparar entrevista"})
    assert update.status_code == 200
    assert update.json()["status"] == "interview"

    history = client.get(f"/api/applications/{app_id}/history", headers=auth_headers)
    assert history.status_code == 200
    assert len(history.json()) >= 2

    cv = client.post(f"/api/cv/jobs/{job_id}", headers=auth_headers)
    assert cv.status_code == 200
    assert "Analista de Dados" in cv.json()["content_md"]

    interview = client.get(f"/api/interview/jobs/{job_id}", headers=auth_headers)
    assert interview.status_code == 200
    assert len(interview.json()["questions"]) >= 5

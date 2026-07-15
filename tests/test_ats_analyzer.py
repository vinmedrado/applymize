from io import BytesIO

from backend.services.ats_analyzer import grade_from_score


RESUME = """
Vinicius Santos Medrado
vinicius@example.com | (11) 99999-9999
https://linkedin.com/in/vinicius-demo
https://github.com/vinmedrado

Resumo
Analista de Dados e Automação com experiência em Python, SQL, FastAPI, PostgreSQL, Docker, Power BI, APIs e ETL.

Skills
Python, SQL, FastAPI, PostgreSQL, Docker, Power BI, Pandas, APIs, ETL

Experiência
Analista de Dados - Empresa X
- Criei automações em Python.
- Desenvolvi dashboards em Power BI.

Projetos
Applymize - sistema com FastAPI, React, PostgreSQL e Docker.

Educação
Curso de Python e Dados

Certificações
Python, Power BI, SQL
"""


def complete_profile(client, auth_headers):
    files = {"file": ("resume.txt", BytesIO(RESUME.encode("utf-8")), "text/plain")}
    upload = client.post("/api/profile/upload-resume", headers=auth_headers, files=files)
    assert upload.status_code == 200, upload.text


def test_ats_grade_mapping():
    assert grade_from_score(97) == "A+"
    assert grade_from_score(88) == "A"
    assert grade_from_score(75) == "B"
    assert grade_from_score(60) == "C"
    assert grade_from_score(45) == "D"
    assert grade_from_score(20) == "F"


def test_ats_analyze_me(client, auth_headers):
    complete_profile(client, auth_headers)
    response = client.get("/api/ats/analyze-me", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["final_score"] >= 0
    assert payload["grade"] in ["A+", "A", "B", "C", "D", "F"]
    assert payload["strengths"]
    assert "ats_score" in payload
    assert "rh_score" in payload


def test_ats_analyze_job(client, auth_headers):
    complete_profile(client, auth_headers)
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend FastAPI Data Engineer",
        "company": "Tech",
        "description": "Python FastAPI PostgreSQL Docker APIs ETL",
        "requirements": "Python, FastAPI, PostgreSQL, Docker, APIs",
        "seniority": "mid",
        "remote": True,
        "location": "Remote",
        "url": "https://remoteok.com/test-ats-job",
        "source": "manual",
        "external_id": "ats-job-1",
    })
    assert job.status_code == 200, job.text

    response = client.get(f"/api/ats/analyze-job/{job.json()['id']}", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["compared_job_id"] == job.json()["id"]
    assert "keyword_score" in payload
    assert "missing_keywords" in payload
    assert payload["suggestions"]


def test_ats_incomplete_profile(client, auth_headers):
    response = client.get("/api/ats/analyze-me", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["warnings"]
    assert payload["final_score"] >= 0


def test_ats_missing_keywords_and_suggestions(client, auth_headers):
    complete_profile(client, auth_headers)
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Kubernetes Scala Engineer",
        "company": "Hard Tech",
        "description": "Kubernetes Scala Kafka Terraform AWS",
        "requirements": "Kubernetes, Scala, Kafka, Terraform, AWS",
        "seniority": "senior",
        "remote": True,
        "location": "Remote",
        "url": "https://example.com/hard-job",
        "source": "manual",
        "external_id": "ats-job-2",
    })
    assert job.status_code == 200
    response = client.get(f"/api/ats/analyze-job/{job.json()['id']}", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["missing_keywords"]
    assert payload["suggestions"]

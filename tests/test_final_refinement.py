from io import BytesIO

from backend.services.resume_parser import parse_resume_text


REALISTIC_RESUME = """
Vinicius Santos Medrado
vinicius@example.com | (11) 99999-9999
https://linkedin.com/in/vinicius-demo
https://github.com/vinmedrado

Resumo
Analista de Dados e Automação com experiência em Python, SQL, FastAPI, PostgreSQL, Docker, Power BI, APIs e ETL.

Skills
Python, SQL, FastAPI, PostgreSQL, Docker, Power BI, Pandas, APIs, ETL, Machine Learning

Experiência
Analista de Dados - Empresa X
- Criei automações em Python que reduziram tarefas manuais.
- Desenvolvi dashboards em Power BI e pipelines SQL.

Projetos
Applymize - sistema de carreira com FastAPI, React, PostgreSQL e Docker.
Pipeline ETL - coleta, transformação e validação de dados.

Educação
Curso de Python, Dados e BI

Idiomas
Português nativo, Inglês técnico

Certificações
Python, Power BI, SQL
"""


def test_parser_realistic_txt():
    parsed = parse_resume_text(REALISTIC_RESUME)
    assert parsed["probable_name"] == "Vinicius Santos Medrado"
    assert parsed["email"] == "vinicius@example.com"
    assert parsed["phone"]
    assert parsed["linkedin"]
    assert parsed["github"]
    assert "Python" in parsed["skills"]
    assert parsed["projects"]
    assert parsed["education"]
    assert parsed["languages"]
    assert parsed["certifications"]


def test_matching_cv_interview_with_real_profile(client, auth_headers):
    files = {"file": ("resume.txt", BytesIO(REALISTIC_RESUME.encode("utf-8")), "text/plain")}
    upload = client.post("/api/profile/upload-resume", headers=auth_headers, files=files)
    assert upload.status_code == 200, upload.text

    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend FastAPI Data Engineer",
        "company": "Tech",
        "description": "Python FastAPI PostgreSQL Docker APIs ETL",
        "requirements": "Python, FastAPI, PostgreSQL, Docker, APIs",
        "seniority": "mid",
        "remote": True,
        "location": "Remote"
    })
    assert job.status_code == 200
    job_id = job.json()["id"]

    strategy = client.get("/api/strategy/recommendations", headers=auth_headers)
    assert strategy.status_code == 200
    assert strategy.json()[0]["factors"]["match_score"] > 0

    cv = client.post(f"/api/cv/jobs/{job_id}", headers=auth_headers)
    assert cv.status_code == 200
    assert "Palavras-chave" in cv.json()["content_md"]
    assert "Vinicius Santos Medrado" in cv.json()["content_md"]

    interview = client.get(f"/api/interview/jobs/{job_id}", headers=auth_headers)
    assert interview.status_code == 200
    assert interview.json()["questions"]

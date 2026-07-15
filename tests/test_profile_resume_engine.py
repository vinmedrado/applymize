from io import BytesIO


def test_create_edit_profile(client, auth_headers):
    response = client.put("/api/profile/me", headers=auth_headers, json={
        "full_name": "User Profile", "professional_title": "Analista de Dados",
        "summary": "Resumo com Python e SQL", "location": "Santo André",
        "work_preferences": "remote,hybrid", "salary_expectation": 8000,
        "phone": "11999999999", "email": "profile@test.com"
    })
    assert response.status_code == 200, response.text
    assert response.json()["professional_title"] == "Analista de Dados"


def test_add_skills(client, auth_headers):
    response = client.post("/api/profile/skills", headers=auth_headers, json={"name": "Python", "level": "advanced", "category": "technical"})
    assert response.status_code == 200
    assert any(skill["name"] == "Python" for skill in response.json()["skills"])


def test_upload_txt_and_parse_resume(client, auth_headers):
    content = b"Vinicius Demo\nvinicius@example.com\n11999999999\nPython SQL FastAPI PostgreSQL Docker Power BI\nExperiencia: Analista de Dados\nProjeto: Sistema Applymize"
    files = {"file": ("resume.txt", BytesIO(content), "text/plain")}
    upload = client.post("/api/profile/upload-resume", headers=auth_headers, files=files)
    assert upload.status_code == 200, upload.text
    assert "Python" in upload.json()["extracted_text"]
    parsed = client.post("/api/profile/parse-resume", headers=auth_headers)
    assert parsed.status_code == 200
    assert "Python" in parsed.json()["parsed_data"]["skills"]


def test_profile_empty_fallback(client, auth_headers):
    response = client.get("/api/profile/me", headers=auth_headers)
    assert response.status_code == 200


def test_cv_uses_profile(client, auth_headers):
    client.put("/api/profile/me", headers=auth_headers, json={
        "full_name": "Perfil Real", "professional_title": "Engenheiro de Dados",
        "summary": "Resumo real", "location": "SP", "work_preferences": "remote",
        "salary_expectation": 9000, "phone": "11999999999", "email": "real@example.com"
    })
    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Data Engineer", "company": "Data", "description": "Python SQL ETL",
        "requirements": "Python, SQL", "seniority": "mid", "remote": True
    })
    cv = client.post(f"/api/cv/jobs/{job.json()['id']}", headers=auth_headers)
    assert cv.status_code == 200
    assert "Perfil Real" in cv.json()["content_md"]

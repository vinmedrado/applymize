from backend.services.translation_service import (
    detect_language,
    dictionary_translate_en_to_pt,
    normalize_free_text,
    normalize_job_text,
)


def test_english_text_translated_to_portuguese():
    result = normalize_job_text(
        "Senior Data Analyst",
        "We are looking for experience with Python, SQL, API and Power BI. Remote job.",
    )
    assert result["translated"] is True
    assert "analista" in result["title"].lower() or "dados" in result["title"].lower()
    assert "Python" in result["description"]
    assert "SQL" in result["description"]
    assert "Power BI" in result["description"]
    assert "remot" in result["description"].lower()


def test_portuguese_text_is_kept():
    result = normalize_job_text(
        "Analista de Dados",
        "Vaga remota para pessoa com experiência em Python, SQL e Power BI.",
    )
    assert result["translated"] is False
    assert result["title"] == "Analista de Dados"
    assert result["description"] == "Vaga remota para pessoa com experiência em Python, SQL e Power BI."


def test_technical_terms_are_preserved():
    translated = dictionary_translate_en_to_pt("Machine Learning engineer with Python, SQL, API, FastAPI and Power BI")
    assert "Machine Learning" in translated
    assert "Python" in translated
    assert "SQL" in translated
    assert "API" in translated
    assert "FastAPI" in translated
    assert "Power BI" in translated


def test_fallback_without_error_for_empty_text():
    result = normalize_free_text("")
    assert result.original_text == ""
    assert result.normalized_text == ""
    assert result.language == "unknown"


def test_job_original_fields_are_kept_on_create(client, auth_headers):
    response = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend Developer",
        "company": "Tech Corp",
        "description": "We are looking for experience with Python and SQL.",
        "requirements": "Python, SQL",
        "location": "Remote",
        "url": "https://example.com/job",
        "source": "manual",
        "external_id": "translation-test-1",
        "remote": True,
    })
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["title_original"] == "Backend Developer"
    assert payload["description_original"] == "We are looking for experience with Python and SQL."
    assert payload["title"] != ""
    assert "Python" in payload["description"]

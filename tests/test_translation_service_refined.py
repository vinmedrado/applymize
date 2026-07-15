from backend.services.translation_service import (
    clear_translation_cache,
    normalize_free_text,
    normalize_job_text,
    translation_cache_size,
    translate_en_to_pt,
)


def test_pipeline_role_dictionary_strong_mapping():
    assert translate_en_to_pt("Software Engineer") == "Engenheiro de Software"
    assert translate_en_to_pt("Data Analyst") == "Analista de Dados"
    assert translate_en_to_pt("Backend Developer") == "Desenvolvedor Backend"
    assert translate_en_to_pt("Frontend Developer") == "Desenvolvedor Frontend"


def test_technical_terms_are_protected_and_restored():
    text = "Backend Developer with Python, SQL, API, FastAPI, Power BI and Machine Learning"
    translated = translate_en_to_pt(text)
    assert "Desenvolvedor Backend" in translated
    assert "Python" in translated
    assert "SQL" in translated
    assert "API" in translated
    assert "FastAPI" in translated
    assert "Power BI" in translated
    assert "Machine Learning" in translated
    assert "Aprendizado de máquina" not in translated


def test_translation_cache_avoids_duplicate_work():
    clear_translation_cache()
    assert translation_cache_size() == 0
    first = normalize_free_text("We are looking for a Data Analyst with Python and SQL")
    second = normalize_free_text("We are looking for a Data Analyst with Python and SQL")
    assert first == second
    assert translation_cache_size() == 1


def test_post_processing_removes_bad_duplication():
    translated = translate_en_to_pt("Data Analyst analyst with with Python")
    assert "with with" not in translated.lower()
    assert "com com" not in translated.lower()
    assert "Analista de Dados" in translated


def test_safe_fallback_empty_and_broken_text():
    result = normalize_free_text("")
    assert result.normalized_text == ""
    assert result.translated is False

    job = normalize_job_text("", "")
    assert job["title"] == ""
    assert job["description"] == ""
    assert job["translated"] is False


def test_portuguese_kept_original():
    result = normalize_job_text("Analista de Dados", "Vaga para trabalhar com Python, SQL e Power BI.")
    assert result["title"] == "Analista de Dados"
    assert result["description"] == "Vaga para trabalhar com Python, SQL e Power BI."
    assert result["translated"] is False

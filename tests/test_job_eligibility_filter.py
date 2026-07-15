"""Regression tests for backend.services.job_eligibility_filter.

These cover the three eligibility bugs found and fixed together:
1. LinkedIn jobs located outside Brazil were never blocked (the function
   was intentionally disabled and returned an empty list unconditionally).
2. The "completo/obrigatório" education blocking list was too narrow and
   missed very common real-world phrasings (e.g. "Superior completo",
   "Nível superior completo").
3. Jobs that explicitly accept an in-progress degree ("cursando",
   "em andamento") were being blocked as if they required a finished one.
"""

from backend.services.job_eligibility_filter import (
    evaluate_job_eligibility,
    linkedin_foreign_blockers,
)


# ---------------------------------------------------------------------------
# LinkedIn foreign-location blocking
# ---------------------------------------------------------------------------

def test_linkedin_job_in_united_states_is_blocked():
    job = {
        "source": "linkedin",
        "title": "Software Engineer",
        "location": "United States",
        "description": "Remote - US only",
        "url": "https://linkedin.com/jobs/123",
    }
    blockers = linkedin_foreign_blockers(job)
    assert blockers, "US LinkedIn job should be blocked"
    assert evaluate_job_eligibility(job)["eligible"] is False


def test_linkedin_job_in_brazil_is_not_blocked():
    job = {
        "source": "linkedin",
        "title": "Engenheiro de Software",
        "location": "São Paulo, Brazil",
        "description": "Remote Brazil",
        "url": "https://linkedin.com/jobs/456",
    }
    assert linkedin_foreign_blockers(job) == []
    assert evaluate_job_eligibility(job)["eligible"] is True


def test_linkedin_worldwide_job_is_blocked():
    job = {
        "source": "linkedin",
        "title": "Dev",
        "location": "Worldwide",
        "description": "Work from anywhere",
        "url": "https://linkedin.com/jobs/789",
    }
    assert linkedin_foreign_blockers(job)


def test_non_linkedin_source_is_never_blocked_by_this_rule():
    # The LinkedIn-specific rule must not affect other providers, even if
    # their text also mentions a foreign country.
    job = {
        "source": "gupy",
        "title": "Analyst",
        "location": "United States",
        "description": "x",
        "url": "https://gupy.io/1",
    }
    assert linkedin_foreign_blockers(job) == []


# ---------------------------------------------------------------------------
# Education requirement blocking ("completo" vs "cursando")
# ---------------------------------------------------------------------------

def test_mandatory_completed_degree_blocks():
    job = {
        "title": "Analista",
        "description": "Requisitos: Ensino superior completo em Administração.",
    }
    result = evaluate_job_eligibility(job)
    assert result["eligible"] is False
    assert "superior_completo_obrigatorio" in result["blockers"]


def test_wider_phrasing_of_completed_degree_also_blocks():
    # Regression: previously only exact phrases like "ensino superior
    # completo" were recognized, so common variants slipped through.
    job = {"title": "Analista", "description": "Nível superior completo obrigatório."}
    result = evaluate_job_eligibility(job)
    assert result["eligible"] is False
    assert "superior_completo_obrigatorio" in result["blockers"]


def test_degree_in_progress_is_accepted_when_job_allows_it():
    job = {
        "title": "Analista",
        "description": "Requisitos: Ensino superior completo ou cursando.",
    }
    result = evaluate_job_eligibility(job)
    assert result["eligible"] is True
    assert result["blockers"] == []


def test_degree_mentioned_only_as_nice_to_have_does_not_block():
    job = {"title": "Analista", "description": "Superior completo é um diferencial."}
    result = evaluate_job_eligibility(job)
    assert result["eligible"] is True


def test_job_explicitly_for_students_in_progress_is_not_blocked():
    job = {
        "title": "Analista",
        "description": "Ensino superior cursando a partir do 5º semestre.",
    }
    result = evaluate_job_eligibility(job)
    assert result["eligible"] is True
    assert result["blockers"] == []


def test_job_without_any_education_requirement_is_eligible():
    job = {"title": "Analista", "description": "Boa comunicação e organização."}
    result = evaluate_job_eligibility(job)
    assert result["eligible"] is True
    assert result["blockers"] == []

from datetime import datetime

from backend.models.job import Job
from backend.services.strategy_engine import (
    calculate_strategy_for_job,
    classify_priority,
    competition_score,
    get_strategy_recommendations,
    weighted_score,
    StrategyFactors,
)


def create_job(client, auth_headers, payload):
    response = client.post("/api/jobs/", headers=auth_headers, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_strategy_weighted_score_and_priority():
    factors = StrategyFactors(
        match_score=90,
        recency_score=90,
        competition_score=80,
        location_score=90,
        remote_score=100,
        seniority_score=90,
    )
    score = weighted_score(factors)
    assert score >= 85
    assert classify_priority(score) == "HIGH_PRIORITY"
    assert classify_priority(65) == "MEDIUM_PRIORITY"
    assert classify_priority(40) == "LOW_PRIORITY"


def test_competition_score_specific_beats_generic():
    generic = Job(
        tenant_id=1,
        title="Analista",
        company="Generic",
        description="Vaga genérica para analista",
        requirements="",
        source="test",
        external_id="generic",
    )
    specific = Job(
        tenant_id=1,
        title="Backend FastAPI PostgreSQL Developer",
        company="Specific",
        description="Python FastAPI PostgreSQL Docker APIs SQL",
        requirements="Python, FastAPI, PostgreSQL, Docker",
        source="test",
        external_id="specific",
        remote=False,
    )
    assert competition_score(specific) > competition_score(generic)


def test_strategy_endpoint_returns_data(client, auth_headers):
    job = create_job(client, auth_headers, {
        "title": "Backend FastAPI Developer",
        "company": "Tech",
        "description": "Python FastAPI PostgreSQL Docker APIs",
        "requirements": "Python, FastAPI, PostgreSQL, Docker",
        "seniority": "mid",
        "remote": True,
        "location": "Remote"
    })

    response = client.get("/api/strategy/recommendations", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["job_id"] == job["id"]
    assert "strategy_score" in payload[0]
    assert payload[0]["priority"] in {"HIGH_PRIORITY", "MEDIUM_PRIORITY", "LOW_PRIORITY"}
    assert "factors" in payload[0]


def test_strategy_with_few_jobs(client, auth_headers):
    create_job(client, auth_headers, {
        "title": "Analista de Dados",
        "company": "Data",
        "description": "SQL Power BI Python",
        "requirements": "SQL, Python",
        "seniority": "mid",
        "remote": True
    })
    response = client.get("/api/strategy/recommendations?limit=5", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_strategy_without_history_or_jobs(client, auth_headers):
    response = client.get("/api/strategy/recommendations", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

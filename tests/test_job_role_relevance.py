from datetime import datetime
from unittest.mock import patch

from backend.core.database import SessionLocal
from backend.models.automation import AutomationSettings
from backend.models.user import User
from backend.services.automation_scheduler import _run_pipeline_for_setting
from backend.services.job_role_relevance import (
    evaluate_role_relevance,
    provider_search_terms,
    role_search_terms,
)
from backend.services.providers.base import ProviderJob


def test_process_automation_role_expands_to_bounded_provider_queries():
    all_terms = role_search_terms("Automação de Processos")
    provider_terms = provider_search_terms("Automação de Processos")

    assert "Automação de Processos" in all_terms
    assert "Analista de Processos" in all_terms
    assert "RPA" in all_terms
    assert "Power Automate" in all_terms
    assert 1 <= len(provider_terms) <= 4


def test_data_job_is_not_relevant_to_process_automation():
    result = evaluate_role_relevance(
        "Automação de Processos",
        {
            "title": "Analista de Dados Sênior",
            "description": "Power BI, SQL, dashboards e indicadores.",
            "requirements": "SQL, Python, Power BI",
        },
    )
    assert result.relevant is False
    assert result.score < 55


def test_process_and_rpa_jobs_are_relevant():
    direct = evaluate_role_relevance(
        "Automação de Processos",
        {"title": "Analista de Processos", "description": "Mapeamento BPM e melhoria contínua."},
    )
    correlated = evaluate_role_relevance(
        "Automação de Processos",
        {
            "title": "Analista de Operações",
            "description": "Automação de workflows, RPA e melhoria contínua dos processos.",
        },
    )
    assert direct.relevant is True
    assert direct.score >= 90
    assert correlated.relevant is True


def test_industrial_automation_and_other_business_areas_are_rejected():
    industrial = evaluate_role_relevance(
        "Automação de Processos",
        {"title": "Engenheiro de Automação Sênior", "description": "CLP, SCADA e processos industriais."},
    )
    accounting = evaluate_role_relevance(
        "Automação de Processos",
        {"title": "Analista de Processos e Sucesso do Cliente - Área Contábil", "description": "BPM e automação."},
    )
    scholarship = evaluate_role_relevance(
        "Automação de Processos",
        {"title": "Bolsista Mestre - Automação de Processos", "description": "Pesquisa em IA."},
    )
    assert industrial.relevant is False
    assert accounting.relevant is False
    assert scholarship.relevant is False


def test_profile_title_updates_auth_target_role(client, auth_headers):
    response = client.put(
        "/api/profile/me",
        headers=auth_headers,
        json={"professional_title": "Automação de Processos"},
    )
    assert response.status_code == 200, response.text

    me = client.get("/api/auth/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["target_role"] == "Automação de Processos"


def test_job_list_hides_irrelevant_external_jobs_but_can_reveal_them(client, auth_headers):
    client.put(
        "/api/profile/me",
        headers=auth_headers,
        json={"professional_title": "Automação de Processos"},
    )
    relevant = client.post(
        "/api/jobs/",
        headers=auth_headers,
        json={
            "title": "Analista de Processos",
            "company": "Process Co",
            "description": "BPM, automação e melhoria contínua",
            "source": "linkedin",
            "external_id": "process-role-1",
        },
    )
    irrelevant = client.post(
        "/api/jobs/",
        headers=auth_headers,
        json={
            "title": "Analista de Dados Sênior",
            "company": "Data Co",
            "description": "SQL, Power BI e dashboards",
            "source": "linkedin",
            "external_id": "data-role-1",
        },
    )
    assert relevant.status_code == 200
    assert irrelevant.status_code == 200

    visible = client.get("/api/jobs/paged", headers=auth_headers).json()
    assert [job["title"] for job in visible["items"]] == ["Analista de Processos"]
    assert visible["hidden_irrelevant"] == 1
    assert visible["items"][0]["role_relevance_score"] >= 90

    all_jobs = client.get("/api/jobs/paged?include_irrelevant=true", headers=auth_headers).json()
    assert all_jobs["total"] == 2

    dashboard = client.get("/api/dashboard/summary", headers=auth_headers)
    analytics = client.get("/api/analytics/overview", headers=auth_headers)
    assert dashboard.status_code == 200
    assert analytics.status_code == 200
    assert dashboard.json()["total_jobs"] == 1
    assert analytics.json()["jobs_total"] == 1


def test_automation_settings_expose_per_user_search_terms(client, auth_headers):
    client.put(
        "/api/profile/me",
        headers=auth_headers,
        json={"professional_title": "Automação de Processos"},
    )
    payload = {
        "enabled": False,
        "mode": "interval",
        "interval_minutes": 60,
        "times": None,
        "window_start": None,
        "window_end": None,
        "search_terms": ["Automação de Processos", "RPA"],
        "min_role_relevance": 65,
    }
    response = client.put("/api/automation/settings", headers=auth_headers, json=payload)
    assert response.status_code == 200, response.text
    assert response.json()["search_terms"] == payload["search_terms"]
    assert response.json()["min_role_relevance"] == 65


def test_ingestion_discards_provider_noise_before_saving(client, auth_headers):
    client.put(
        "/api/profile/me",
        headers=auth_headers,
        json={"professional_title": "Automação de Processos"},
    )
    provider_jobs = [
        ProviderJob(
            source="gupy",
            external_id="good-process",
            title="Analista de Processos",
            company="Process Co",
            location="São Paulo",
            description="BPM, RPA e melhoria contínua",
        ),
        ProviderJob(
            source="gupy",
            external_id="bad-data",
            title="Analista de Dados Sênior",
            company="Data Co",
            location="São Paulo",
            description="SQL, Power BI e dashboards",
        ),
    ]
    with patch("backend.services.providers.gupy.GupyProvider.fetch_jobs", return_value=provider_jobs):
        response = client.post(
            "/api/jobs/ingest?provider=gupy&term=Automação%20de%20Processos",
            headers=auth_headers,
        )

    assert response.status_code == 200, response.text
    assert response.json()["inserted"] == 1
    assert [job["title"] for job in response.json()["jobs"]] == ["Analista de Processos"]


def test_scheduler_uses_user_terms_instead_of_global_data_default(client, auth_headers):
    client.put(
        "/api/profile/me",
        headers=auth_headers,
        json={"professional_title": "Automação de Processos"},
    )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "user@test.com").first()
        setting = AutomationSettings(
            user_id=user.id,
            enabled=True,
            mode="interval",
            interval_minutes=60,
            search_terms=["Automação de Processos", "RPA"],
            min_role_relevance=60,
        )
        db.add(setting)
        db.commit()
        db.refresh(setting)

        fake_session = type("Session", (), {"phone_number": "5511999999999"})()
        with (
            patch("backend.services.automation_scheduler._tenant_id_for_user", return_value=1),
            patch("backend.services.automation_scheduler._user_whatsapp_session", return_value=fake_session),
            patch("backend.services.automation_scheduler._default_provider", return_value="gupy"),
            patch("backend.services.automation_scheduler.ingest_jobs", return_value=(0, 0, [], {}, {})) as ingest,
            patch("backend.services.automation_scheduler._select_jobs_to_send", return_value=[]),
        ):
            _run_pipeline_for_setting(db, setting, datetime.utcnow())

        terms = [call.kwargs["provider_options"]["term"] for call in ingest.call_args_list]
        assert terms == ["Automação de Processos", "RPA"]
        assert "Analista de Dados" not in terms
    finally:
        db.close()

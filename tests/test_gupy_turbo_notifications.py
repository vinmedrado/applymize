from unittest.mock import patch

from backend.services.providers.gupy import GupyProvider


def test_gupy_build_params_dynamic_no_region_locked():
    provider = GupyProvider()
    params = provider.build_search_params(limit=15)
    assert params["limit"] == 15
    assert "state" not in params
    assert "city[]" not in params
    assert not any(str(value).lower() in {"rj", "rio de janeiro", "sp", "são paulo"} for value in params.values())

    filtered = provider.build_search_params(
        term="Analista de dados",
        state="São Paulo",
        city="Santo André",
        workplace_types="remote,hybrid",
        limit=10,
    )
    assert filtered["jobName"] == "Analista de dados"
    assert filtered["state"] == "São Paulo"
    assert filtered["city"] == "Santo André"
    assert filtered["workplaceTypes"] == "remote,hybrid"


def test_gupy_normalization_and_dedup_fetch():
    provider = GupyProvider()
    payload = {
        "data": [
            {
                "id": "1",
                "name": "Analista de Dados",
                "careerPage": {"name": "Empresa A"},
                "city": "São Paulo",
                "state": "SP",
                "workplaceType": "remote",
                "description": "<p>Python SQL</p>",
                "jobUrl": "https://portal.gupy.io/job/1",
            },
            {
                "id": "1",
                "name": "Analista de Dados",
                "careerPage": {"name": "Empresa A"},
                "city": "São Paulo",
                "state": "SP",
                "workplaceType": "remote",
                "description": "<p>Python SQL</p>",
                "jobUrl": "https://portal.gupy.io/job/1",
            },
        ]
    }

    class FakeResponse:
        status_code = 200
        text = ""
        url = "https://employability-portal.gupy.io/api/v1/jobs"

        def raise_for_status(self):
            return None

        def json(self):
            return payload

    with patch("backend.services.providers.gupy.requests.get", return_value=FakeResponse()):
        jobs = provider.fetch_jobs(limit=10, term="dados")
        assert len(jobs) == 1
        assert jobs[0].source == "gupy"
        assert jobs[0].url == "https://portal.gupy.io/job/1"
        assert jobs[0].remote is True


def test_notifications_settings_disabled(client, auth_headers):
    response = client.get("/api/notifications/settings", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["enabled"] is False
    assert "telegram" in payload
    assert "whatsapp_evolution" in payload


def test_notification_test_without_credentials_does_not_break(client, auth_headers):
    response = client.post("/api/notifications/test", headers=auth_headers)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["sent"] == 0
    assert payload["enabled"] is False


def test_notification_duplicate_block_and_limit(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.notification_center.settings.notifications_enabled", True)
    monkeypatch.setattr("backend.services.notification_center.settings.notification_max_per_run", 1)
    monkeypatch.setattr("backend.services.notification_center.settings.notification_min_priority", "HIGH")

    job = client.post("/api/jobs/", headers=auth_headers, json={
        "title": "Backend FastAPI Data Engineer",
        "company": "Notify Tech",
        "description": "Python FastAPI PostgreSQL Docker APIs ETL",
        "requirements": "Python, FastAPI, PostgreSQL, Docker, APIs",
        "seniority": "mid",
        "remote": True,
        "location": "Remote",
        "url": "https://remoteok.com/notify-job",
        "source": "manual",
        "external_id": "notify-job-1",
    })
    assert job.status_code == 200

    client.put("/api/profile/me", headers=auth_headers, json={
        "full_name": "Notify User",
        "professional_title": "Backend Python",
        "summary": "Python FastAPI PostgreSQL Docker APIs ETL",
        "location": "Remote",
        "work_preferences": "remote",
        "salary_expectation": 8000,
        "phone": "11999999999",
        "email": "notify@example.com",
    })
    client.post("/api/profile/skills", headers=auth_headers, json={"name": "Python", "level": "advanced", "category": "technical"})
    client.post("/api/profile/skills", headers=auth_headers, json={"name": "FastAPI", "level": "advanced", "category": "technical"})
    client.post("/api/profile/skills", headers=auth_headers, json={"name": "PostgreSQL", "level": "advanced", "category": "technical"})

    class FakeResult:
        channel = "telegram"
        status = "sent"
        message = "ok"
        error_message = ""

    with patch("backend.services.notifiers.telegram_notifier.TelegramNotifier.is_configured", return_value=True), \
         patch("backend.services.notifiers.telegram_notifier.TelegramNotifier.send_message", return_value=FakeResult()), \
         patch("backend.services.notifiers.whatsapp_evolution_notifier.WhatsAppEvolutionNotifier.is_configured", return_value=False):
        first = client.post("/api/notifications/send-high-priority", headers=auth_headers)
        assert first.status_code == 200, first.text
        assert first.json()["selected"] <= 1

        second = client.post("/api/notifications/send-high-priority", headers=auth_headers)
        assert second.status_code == 200, second.text
        assert second.json()["skipped"] >= 1 or second.json()["sent"] == 0

from unittest.mock import patch

from backend.services.providers.base import ProviderJob


def test_providers_registry(client, auth_headers):
    response = client.get("/api/providers", headers=auth_headers)
    assert response.status_code == 200
    names = {item["provider"] for item in response.json()}
    assert {"remoteok", "gupy", "vagas"}.issubset(names)


def test_providers_health(client, auth_headers):
    response = client.get("/api/providers/health", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()


def test_invalid_provider(client, auth_headers):
    response = client.post("/api/jobs/ingest?provider=invalid", headers=auth_headers)
    assert response.status_code == 400


def test_remoteok_ingestion_and_dedup(client, auth_headers):
    fake_jobs = [
        ProviderJob(
            source="remoteok",
            external_id="remoteok-test-1",
            title="Python Developer",
            company="Remote Test",
            location="Remote",
            url="https://remoteok.com/test-1",
            description="Python FastAPI SQL",
            requirements="Python, FastAPI",
            seniority="mid",
            employment_type="full_time",
            salary_min=0,
            salary_max=0,
            remote=True,
        )
    ]

    with patch("backend.services.providers.remoteok.RemoteOKProvider.fetch_jobs", return_value=fake_jobs):
        first = client.post("/api/jobs/ingest?provider=remoteok&limit=1", headers=auth_headers)
        assert first.status_code == 200, first.text
        assert first.json()["inserted"] == 1
        assert first.json()["skipped"] == 0

        second = client.post("/api/jobs/ingest?provider=remoteok&limit=1", headers=auth_headers)
        assert second.status_code == 200, second.text
        assert second.json()["inserted"] == 0
        assert second.json()["skipped"] == 1


def test_ingest_all(client, auth_headers):
    fake_remote = [
        ProviderJob(
            source="remoteok",
            external_id="remoteok-all-1",
            title="Backend Python",
            company="Remote",
            location="Remote",
            url="https://remoteok.com/all-1",
            description="Python",
            requirements="Python",
            remote=True,
        )
    ]
    fake_gupy = [
        ProviderJob(
            source="gupy",
            external_id="gupy-all-1",
            title="Analista Dados",
            company="GupyCo",
            location="Brasil",
            url="https://portal.gupy.io/job/1",
            description="SQL",
            requirements="SQL",
            remote=True,
        )
    ]
    fake_vagas = [
        ProviderJob(
            source="vagas",
            external_id="vagas-all-1",
            title="Data Engineer",
            company="VagasCo",
            location="SP",
            url="https://www.vagas.com.br/vagas/1",
            description="ETL",
            requirements="ETL",
            remote=False,
        )
    ]

    with patch("backend.services.providers.remoteok.RemoteOKProvider.fetch_jobs", return_value=fake_remote), \
         patch("backend.services.providers.gupy.GupyProvider.fetch_jobs", return_value=fake_gupy), \
         patch("backend.services.providers.vagas.VagasProvider.fetch_jobs", return_value=fake_vagas), \
         patch("backend.services.providers.jobspy_provider.JobSpyProvider.fetch_jobs", return_value=[]), \
         patch("backend.services.providers.linkedin_guest.LinkedInGuestProvider.fetch_jobs", return_value=[]), \
         patch("backend.services.providers.infojobs.InfoJobsProvider.fetch_jobs", return_value=[]):
        response = client.post("/api/jobs/ingest?provider=all&limit=1", headers=auth_headers)
        assert response.status_code == 200, response.text
        # The authenticated test user targets Backend Python. Provider noise
        # from unrelated Data/BI searches must be discarded before storage.
        assert response.json()["inserted"] == 1
        assert response.json()["jobs"][0]["title"] == "Backend Python"
        assert response.json()["collected_by_provider"]["remoteok"] == 1
        assert response.json()["collected_by_provider"]["gupy"] == 0
        assert response.json()["collected_by_provider"]["vagas"] == 0

from unittest.mock import patch

from backend.services.providers.base import ProviderJob
from backend.services.providers.gupy import GupyProvider
from backend.services.providers.vagas import VagasProvider


def test_providers_requires_jwt(client):
    response = client.get("/api/providers")
    assert response.status_code == 401

    health = client.get("/api/providers/health")
    assert health.status_code == 401


def test_gupy_build_search_params_dynamic():
    provider = GupyProvider()
    params = provider.build_search_params(
        term="Analista de dados",
        state="São Paulo",
        city="Santo André",
        workplace_types="remote,hybrid",
        limit=10,
    )
    assert params["jobName"] == "Analista de dados"
    assert params["state"] == "São Paulo"
    assert params["city"] == "Santo André"
    assert params["workplaceTypes"] == "remote,hybrid"
    assert params["limit"] == 10

    url = provider.build_search_url(
        term="Analista de dados",
        state="São Paulo",
        city="Santo André",
        workplace_types="remote,hybrid",
    )
    assert "term=Analista" in url
    assert "state=" in url


def test_vagas_build_search_url_dynamic():
    provider = VagasProvider()
    url = provider.build_search_url("Analista de dados")
    assert "vagas-de-analista-de-dados" in url


def test_healthcheck_resilient_without_external_call(client, auth_headers):
    response = client.get("/api/providers/health", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert all("provider" in item for item in payload)
    assert all("message" in item for item in payload)


def test_invalid_provider_still_returns_400(client, auth_headers):
    response = client.post("/api/jobs/ingest?provider=invalid", headers=auth_headers)
    assert response.status_code == 400


def test_gupy_ingest_with_filters(client, auth_headers):
    fake_jobs = [
        ProviderJob(
            source="gupy",
            external_id="gupy-filter-1",
            title="Analista de Dados",
            company="Gupy Test",
            location="São Paulo",
            url="https://portal.gupy.io/job/1",
            description="SQL Power BI Python",
            requirements="SQL, Python",
            seniority="mid",
            remote=True,
        )
    ]

    with patch("backend.services.providers.gupy.GupyProvider.fetch_jobs", return_value=fake_jobs) as mocked:
        response = client.post(
            "/api/jobs/ingest?provider=gupy&term=Analista%20de%20dados&state=São%20Paulo&city=Santo%20André&workplace_types=remote,hybrid",
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        assert response.json()["inserted"] == 1
        assert mocked.call_args.kwargs["term"] == "Analista de dados"
        assert mocked.call_args.kwargs["state"] == "São Paulo"
        assert mocked.call_args.kwargs["city"] == "Santo André"
        assert mocked.call_args.kwargs["workplace_types"] == "remote,hybrid"


def test_vagas_ingest_with_term(client, auth_headers):
    fake_jobs = [
        ProviderJob(
            source="vagas",
            external_id="vagas-term-1",
            title="Analista de Dados",
            company="Vagas Test",
            location="São Paulo",
            url="https://www.vagas.com.br/vagas/1",
            description="SQL Power BI",
            requirements="",
            seniority="mid",
            remote=False,
        )
    ]

    with patch("backend.services.providers.vagas.VagasProvider.fetch_jobs", return_value=fake_jobs) as mocked:
        response = client.post("/api/jobs/ingest?provider=vagas&term=Analista%20de%20dados", headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json()["inserted"] == 1
        assert mocked.call_args.kwargs["term"] == "Analista de dados"

def test_health_reports_database_without_exposing_configuration(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"
    assert "cors_origins" not in response.json()


def test_invalid_provider_returns_error(client, auth_headers):
    response = client.post("/api/jobs/ingest?source=invalid&limit=1", headers=auth_headers)
    assert response.status_code == 400
    assert "Provider" in response.text

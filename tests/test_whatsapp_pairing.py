from unittest.mock import patch

from backend.services.whatsapp_session_service import WhatsAppSessionService


def test_whatsapp_status_without_config(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_url", "")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_key", "")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_instance_id", "")

    response = client.get("/api/whatsapp/status", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["configured"] is False
    assert payload["status"] == "not_configured"
    assert "api_key" not in str(payload).lower()


def test_whatsapp_qrcode_returned(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_url", "http://evolution.local")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_key", "SECRET_KEY_SHOULD_NOT_LEAK")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_instance_id", "applymize-test")
    client.post("/api/whatsapp/phone", headers=auth_headers, json={"phone_number": "5511999999999"})

    def fake_request(self, method, path, **kwargs):
        if "connect" in path or "qrcode" in path:
            return True, {"base64": "iVBORw0KGgo" + "A" * 100}
        return True, {"state": "connecting", "qrcode": True}

    with patch.object(WhatsAppSessionService, "request", fake_request):
        response = client.get("/api/whatsapp/qrcode", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["configured"] is True
    assert payload["qrcode"]
    assert "SECRET_KEY_SHOULD_NOT_LEAK" not in str(payload)


def test_whatsapp_evolution_error_does_not_break(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_url", "http://evolution.local")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_key", "SECRET_KEY_SHOULD_NOT_LEAK")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_instance_id", "applymize-test")
    client.post("/api/whatsapp/phone", headers=auth_headers, json={"phone_number": "5511999999999"})

    def fake_request(self, method, path, **kwargs):
        return False, {"error": "offline"}

    with patch.object(WhatsAppSessionService, "request", fake_request):
        response = client.get("/api/whatsapp/status", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "error"
    assert "SECRET_KEY_SHOULD_NOT_LEAK" not in str(payload)


def test_whatsapp_test_blocked_without_number(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_url", "http://evolution.local")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_key", "SECRET_KEY_SHOULD_NOT_LEAK")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_instance_id", "applymize-test")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_target_number", "")

    response = client.post("/api/whatsapp/test", headers=auth_headers, json={"target_number": ""})
    assert response.status_code == 200
    payload = response.json()
    assert payload["sent"] is False
    assert payload["status"] == "phone_missing"
    assert "SECRET_KEY_SHOULD_NOT_LEAK" not in str(payload)


def test_whatsapp_api_key_not_exposed_status(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_url", "http://evolution.local")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_api_key", "SUPER_SECRET_EVOLUTION")
    monkeypatch.setattr("backend.services.whatsapp_session_service.settings.evolution_instance_id", "applymize-test")
    client.post("/api/whatsapp/phone", headers=auth_headers, json={"phone_number": "5511999999999"})

    def fake_request(self, method, path, **kwargs):
        return True, {"state": "open", "apikey": "SUPER_SECRET_EVOLUTION"}

    with patch.object(WhatsAppSessionService, "request", fake_request):
        response = client.get("/api/whatsapp/status", headers=auth_headers)

    assert response.status_code == 200
    assert "SUPER_SECRET_EVOLUTION" not in str(response.json())

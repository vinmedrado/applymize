from backend.services.whatsapp_session_service import WhatsAppSessionService


def test_instance_name_is_tenant_user_scoped():
    svc = WhatsAppSessionService(None)
    assert svc.build_instance_name(10, 20).endswith("_10_20")
    assert svc.build_instance_name(10, 20) != svc.build_instance_name(10, 21)


def test_phone_normalization_adds_default_country_code():
    svc = WhatsAppSessionService(None)
    assert svc.normalize_phone_number("(11) 99999-9999").startswith("55")


def test_extract_qrcode_rejects_non_scannable_short_text():
    svc = WhatsAppSessionService(None)
    qr = svc.extract_qrcode({"qrcode": "abc123"})
    assert qr["qrcode"] == ""
    assert qr["type"] == "none"


def test_sanitize_payload_hides_api_key(monkeypatch):
    svc = WhatsAppSessionService(None)
    svc.api_key = "secret-key"
    payload = {"apikey": "secret-key", "nested": {"token": "abc"}, "text": "secret-key"}
    assert svc.sanitize_payload(payload)["apikey"] == "***"
    assert svc.sanitize_payload(payload)["nested"]["token"] == "***"
    assert "secret-key" not in str(svc.sanitize_payload(payload))

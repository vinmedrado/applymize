from unittest.mock import patch

from backend.core.database import SessionLocal
from backend.models.membership import Membership
from backend.models.user import User
from backend.models.whatsapp_session import WhatsAppSession
from backend.services.notifiers.whatsapp_evolution_notifier import WhatsAppEvolutionNotifier
from backend.services.whatsapp_session_service import WhatsAppSessionService


def test_whatsapp_notifier_requires_user_session(monkeypatch):
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_api_url", "http://evolution.local")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_api_key", "secret")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_instance_id", "applymize")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_target_number", "")

    notifier = WhatsAppEvolutionNotifier()

    assert notifier.is_configured() is False
    result = notifier.send_message("teste")

    assert result.status == "disabled"
    assert "sessão por usuário/tenant" in result.error_message


def test_whatsapp_notifier_sends_through_user_session(client, auth_headers, monkeypatch):
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_api_url", "http://evolution.local")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_api_key", "secret")
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "user@test.com").one()
        membership = db.query(Membership).filter(Membership.user_id == user.id).one()
        db.add(WhatsAppSession(
            tenant_id=membership.tenant_id,
            user_id=user.id,
            instance_name=f"applymize_{membership.tenant_id}_{user.id}",
            phone_number="5511999999999",
            status="connected",
            connected=True,
        ))
        db.commit()

        with patch.object(WhatsAppSessionService, "send_notification_message", return_value=(True, "")) as send:
            notifier = WhatsAppEvolutionNotifier(db, user.id, membership.tenant_id)
            result = notifier.send_message("vaga boa")

        assert notifier.is_configured() is True
        assert result.status == "sent"
        assert send.call_args.args[1] == "vaga boa"
    finally:
        db.close()


def test_whatsapp_notifier_disabled_when_evolution_missing(monkeypatch):
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_api_url", "")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_api_key", "")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_instance_id", "")
    monkeypatch.setattr("backend.services.notifiers.whatsapp_evolution_notifier.settings.evolution_target_number", "5511999999999")

    result = WhatsAppEvolutionNotifier().send_message("teste")

    assert result.status == "disabled"
    assert "Evolution API" in result.error_message

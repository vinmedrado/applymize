from __future__ import annotations

from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.whatsapp_session import WhatsAppSession
from backend.services.notifiers.base import BaseNotifier, NotificationResult
from backend.services.whatsapp_session_service import WhatsAppSessionService


class WhatsAppEvolutionNotifier(BaseNotifier):
    channel_name = "whatsapp_evolution"

    def __init__(self, db: Session | None = None, user_id: int | None = None, tenant_id: int | None = None) -> None:
        self.db = db
        self.user_id = user_id
        self.tenant_id = tenant_id

    def is_configured(self) -> bool:
        api_configured = bool(settings.whatsapp_enabled and settings.evolution_api_url and settings.evolution_api_key)
        if not api_configured:
            return False
        if not self.db or self.user_id is None or self.tenant_id is None:
            return False
        return self.db.query(WhatsAppSession).filter(
            WhatsAppSession.tenant_id == self.tenant_id,
            WhatsAppSession.user_id == self.user_id,
            WhatsAppSession.phone_number != "",
            WhatsAppSession.connected.is_(True),
        ).first() is not None

    def send_message(self, message: str) -> NotificationResult:
        if not (settings.whatsapp_enabled and settings.evolution_api_url and settings.evolution_api_key):
            return NotificationResult(self.channel_name, "disabled", message, "Evolution API não configurada.")
        if not self.db or self.user_id is None or self.tenant_id is None:
            return NotificationResult(self.channel_name, "disabled", message, "WhatsApp exige sessão por usuário/tenant.")
        session = self.db.query(WhatsAppSession).filter(
            WhatsAppSession.tenant_id == self.tenant_id,
            WhatsAppSession.user_id == self.user_id,
        ).first()
        if not session or not session.phone_number:
            return NotificationResult(self.channel_name, "disabled", message, "WhatsApp não configurado. Salve o telefone na tela WhatsApp / Pareamento.")
        ok, error = WhatsAppSessionService(self.db).send_notification_message(session, message)
        if ok:
            return NotificationResult(self.channel_name, "sent", message, "")
        return NotificationResult(self.channel_name, "failed", message, error)

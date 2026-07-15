from __future__ import annotations

import requests

from backend.core.config import settings
from backend.services.notifiers.base import BaseNotifier, NotificationResult


class TelegramNotifier(BaseNotifier):
    channel_name = "telegram"

    def is_configured(self) -> bool:
        return bool(settings.telegram_bot_token and settings.telegram_chat_id)

    def send_message(self, message: str) -> NotificationResult:
        if not self.is_configured():
            return NotificationResult(self.channel_name, "disabled", message, "Telegram não configurado.")
        try:
            response = requests.post(
                f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
                json={"chat_id": settings.telegram_chat_id, "text": message, "disable_web_page_preview": False},
                timeout=15,
            )
            response.raise_for_status()
            return NotificationResult(self.channel_name, "sent", message, "")
        except Exception as exc:
            return NotificationResult(self.channel_name, "failed", message, str(exc))

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NotificationResult:
    channel: str
    status: str
    message: str = ""
    error_message: str = ""


class BaseNotifier:
    channel_name = "base"

    def is_configured(self) -> bool:
        return False

    def send_message(self, message: str) -> NotificationResult:
        return NotificationResult(self.channel_name, "disabled", message, "Canal não configurado.")

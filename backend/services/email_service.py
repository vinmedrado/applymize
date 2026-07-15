from __future__ import annotations

import smtplib
from email.message import EmailMessage

from backend.core.config import settings
from backend.core.logging import get_logger

logger = get_logger(__name__)


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    subject = "Recuperação de senha - Applymize"
    body = (
        "Olá,\n\n"
        "Recebemos uma solicitação para redefinir sua senha no Applymize.\n"
        "Clique no link abaixo para criar uma nova senha:\n\n"
        f"{reset_link}\n\n"
        f"Este link expira em {settings.password_reset_token_minutes} minutos.\n"
        "Se você não solicitou isso, ignore este e-mail.\n"
    )

    if not settings.smtp_host or not settings.smtp_from_email:
        # Never log the reset URL: it contains a credential-equivalent token.
        logger.warning("password_reset_email_not_configured to=%s", to_email)
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        logger.info("password_reset_email_sent to=%s", to_email)
        return True
    except Exception as exc:
        logger.warning("password_reset_email_failed to=%s error=%s", to_email, exc)
        return False

"""Mocks e-mail (MailHog si joignable, sinon journal) et SMS (journal en mémoire)."""

from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText

from flask import current_app

logger = logging.getLogger("app.notifications")

# Journaux en mémoire — inspectables par les tests.
EMAIL_LOG: list[dict] = []
SMS_LOG: list[dict] = []


def send_email(to: str, subject: str, body: str) -> dict:
    record = {"to": to, "subject": subject, "body": body}
    EMAIL_LOG.append(record)
    server = current_app.config.get("MAIL_SERVER")
    port = int(current_app.config.get("MAIL_PORT", 1025))
    sender = current_app.config.get("MAIL_DEFAULT_SENDER", "no-reply@cacaosat.ci")
    try:
        msg = MIMEText(body, _charset="utf-8")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        with smtplib.SMTP(server, port, timeout=2) as smtp:
            smtp.sendmail(sender, [to], msg.as_string())
        record["delivered"] = "smtp"
    except Exception:  # noqa: BLE001 - MailHog absent en test/CI
        record["delivered"] = "log"
        logger.info("EMAIL (mock) -> %s | %s", to, subject)
    return record


def send_sms(to: str, text: str) -> dict:
    record = {"to": to, "text": text, "delivered": "log"}
    SMS_LOG.append(record)
    logger.info("SMS (mock) -> %s | %s", to, text[:80])
    return record


def reset_logs() -> None:
    EMAIL_LOG.clear()
    SMS_LOG.clear()

from __future__ import annotations

import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import settings
from app.db.models import TriggeredAlert


def _format_alert_text(trigger: TriggeredAlert) -> str:
    label = trigger.alert_type.replace("_", " ")
    return (
        f"CryptoPulse alert: {trigger.symbol} {label}\n"
        f"{trigger.message}\n"
        f"Observed value: {trigger.observed_value} | "
        f"Threshold: {trigger.threshold} | "
        f"Triggered at: {trigger.triggered_at:%Y-%m-%d %H:%M:%S} UTC"
    )


def _send_webhook(text: str, trigger: TriggeredAlert) -> bool:
    """POST to a generic webhook. The ``content`` field keeps this compatible
    with Discord and Slack incoming webhooks; the structured ``alert`` block is
    ignored by those services but useful for custom consumers."""
    if not settings.alert_webhook_url:
        return False

    payload = {
        "content": text,
        "alert": {
            "symbol": trigger.symbol,
            "alert_type": trigger.alert_type,
            "threshold": float(trigger.threshold) if trigger.threshold is not None else None,
            "observed_value": float(trigger.observed_value),
            "triggered_at": trigger.triggered_at.isoformat(),
        },
    }
    with httpx.Client(timeout=8) as client:
        response = client.post(settings.alert_webhook_url, json=payload)
        response.raise_for_status()
    return True


def _send_email(text: str, trigger: TriggeredAlert) -> bool:
    if not (settings.smtp_host and settings.smtp_from and settings.alert_email_to):
        return False

    message = EmailMessage()
    label = trigger.alert_type.replace("_", " ")
    message["Subject"] = f"CryptoPulse alert: {trigger.symbol} {label}"
    message["From"] = settings.smtp_from
    message["To"] = settings.alert_email_to
    message.set_content(text)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
    return True


def notify_triggered_alert(trigger: TriggeredAlert) -> list[str]:
    """Dispatch a single triggered alert to every configured channel.

    Best-effort: a channel that is not configured is skipped, and a channel that
    fails is logged but never raises, so notification problems can never break
    alert evaluation.
    """
    text = _format_alert_text(trigger)
    delivered: list[str] = []

    for channel, sender in (("webhook", _send_webhook), ("email", _send_email)):
        try:
            if sender(text, trigger):
                delivered.append(channel)
        except Exception as exc:  # pragma: no cover - network/SMTP failures
            print(f"[notifications] {channel} delivery failed: {exc}")

    return delivered


def notify_triggered_alerts(triggers: list[TriggeredAlert]) -> None:
    for trigger in triggers:
        channels = notify_triggered_alert(trigger)
        if channels:
            print(
                f"[notifications] sent {trigger.symbol} alert via {', '.join(channels)}"
            )

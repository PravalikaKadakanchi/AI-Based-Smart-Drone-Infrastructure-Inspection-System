"""
Email automation: sends the generated PDF inspection report to the
registered recipient via SMTP.

Credentials are read exclusively from environment variables
(app.config.Config) — never hardcode SMTP username/password here.
If credentials aren't configured, `send_report_email` no-ops with a
clear log message instead of raising, so demo/simulation runs don't
require real email setup.
"""

import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path

logger = logging.getLogger(__name__)


def send_report_email(
    smtp_host: str,
    smtp_port: int,
    username: str,
    password: str,
    recipient: str,
    report_path: Path,
    inspection_id: str,
    severity_label: str,
) -> bool:
    if not username or not password or not recipient:
        logger.warning(
            "Email not sent: SMTP credentials or recipient not configured. "
            "Set SMTP_USERNAME, SMTP_PASSWORD, and REPORT_RECIPIENT_EMAIL in your .env file."
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = f"Drone Inspection Report - {inspection_id} - {severity_label}"
    msg["From"] = username
    msg["To"] = recipient
    msg.set_content(
        f"Automated inspection report {inspection_id} is attached.\n\n"
        f"Severity: {severity_label}\n\n"
        "This is an automated message from the AI-Based Smart Drone "
        "Infrastructure Inspection System."
    )

    with open(report_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=Path(report_path).name,
        )

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        logger.info(f"Inspection report emailed to {recipient}.")
        return True
    except Exception as exc:
        logger.error(f"Failed to send email: {exc}")
        return False

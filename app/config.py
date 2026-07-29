"""
Application configuration.

All secrets (email credentials, SMTP settings, etc.) are loaded from
environment variables. NEVER hardcode credentials here.
Copy `.env.example` to `.env` and fill in real values locally.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-key-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    # Hardware / simulation
    # Set to "True" to run without physical Raspberry Pi camera or Pixhawk
    # attached — generates synthetic frames and telemetry for demos/dev.
    SIMULATION_MODE = os.environ.get("SIMULATION_MODE", "True").lower() == "true"

    # MAVLink connection string for Pixhawk (e.g. "/dev/serial0" or "udp:127.0.0.1:14550")
    MAVLINK_CONNECTION = os.environ.get("MAVLINK_CONNECTION", "udp:127.0.0.1:14550")
    MAVLINK_BAUDRATE = int(os.environ.get("MAVLINK_BAUDRATE", "57600"))

    # Vision
    CRACK_DETECTION_THRESHOLD = float(os.environ.get("CRACK_DETECTION_THRESHOLD", "0.35"))

    # Storage
    SAMPLE_IMAGE_DIR = BASE_DIR / "data" / "sample_images"
    INSPECTION_LOG_DIR = BASE_DIR / "data" / "inspection_logs"
    REPORT_OUTPUT_DIR = BASE_DIR / "data" / "inspection_logs"

    # Email (SMTP)
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    REPORT_RECIPIENT_EMAIL = os.environ.get("REPORT_RECIPIENT_EMAIL", "")

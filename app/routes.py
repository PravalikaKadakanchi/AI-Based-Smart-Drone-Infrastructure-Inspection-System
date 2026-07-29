import uuid
import base64
from datetime import datetime

import cv2
from flask import Blueprint, render_template, jsonify, current_app, send_from_directory

from drone.camera import DroneCamera
from drone.telemetry import TelemetryReader
from vision.crack_detector import CrackDetector
from vision.severity_classifier import SeverityClassifier
from reports.pdf_generator import generate_report
from notifications.email_sender import send_report_email

bp = Blueprint("main", __name__)

_crack_detector = CrackDetector()
_severity_classifier = SeverityClassifier()

# Lazily-initialized hardware interfaces (created on first inspection request
# so the app can boot even before config is fully loaded in tests).
_camera = None
_telemetry_reader = None


def _get_camera() -> DroneCamera:
    global _camera
    if _camera is None:
        _camera = DroneCamera(simulation_mode=current_app.config["SIMULATION_MODE"])
    return _camera


def _get_telemetry() -> TelemetryReader:
    global _telemetry_reader
    if _telemetry_reader is None:
        _telemetry_reader = TelemetryReader(
            connection_string=current_app.config["MAVLINK_CONNECTION"],
            baudrate=current_app.config["MAVLINK_BAUDRATE"],
            simulation_mode=current_app.config["SIMULATION_MODE"],
        )
    return _telemetry_reader


@bp.route("/")
def dashboard():
    return render_template("dashboard.html", simulation_mode=current_app.config["SIMULATION_MODE"])


@bp.route("/api/inspect", methods=["POST"])
def run_inspection():
    """Runs one full inspection cycle: capture -> detect -> classify -> report -> email."""
    inspection_id = f"INSP-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

    camera = _get_camera()
    telemetry_reader = _get_telemetry()

    frame = camera.capture_frame()
    telemetry = telemetry_reader.read()

    crack_result = _crack_detector.detect(frame)
    severity = _severity_classifier.classify(crack_result)

    log_dir = current_app.config["INSPECTION_LOG_DIR"]
    log_dir.mkdir(parents=True, exist_ok=True)
    image_path = log_dir / f"{inspection_id}.jpg"
    cv2.imwrite(str(image_path), crack_result.annotated_image)

    report_path = current_app.config["REPORT_OUTPUT_DIR"] / f"{inspection_id}.pdf"
    generate_report(
        output_path=report_path,
        inspection_id=inspection_id,
        image_path=image_path,
        telemetry=telemetry,
        crack_result=crack_result,
        severity=severity,
    )

    email_sent = send_report_email(
        smtp_host=current_app.config["SMTP_HOST"],
        smtp_port=current_app.config["SMTP_PORT"],
        username=current_app.config["SMTP_USERNAME"],
        password=current_app.config["SMTP_PASSWORD"],
        recipient=current_app.config["REPORT_RECIPIENT_EMAIL"],
        report_path=report_path,
        inspection_id=inspection_id,
        severity_label=severity.label,
    )

    _, buffer = cv2.imencode(".jpg", crack_result.annotated_image)
    image_b64 = base64.b64encode(buffer).decode("utf-8")

    return jsonify(
        {
            "inspection_id": inspection_id,
            "timestamp": datetime.fromtimestamp(telemetry.timestamp).isoformat(),
            "gps": {"lat": telemetry.latitude, "lon": telemetry.longitude, "alt_m": telemetry.altitude_m},
            "battery_percent": telemetry.battery_percent,
            "flight_mode": telemetry.flight_mode,
            "crack_detected": crack_result.crack_detected,
            "crack_count": crack_result.crack_count,
            "coverage_percent": round(crack_result.coverage_ratio * 100, 2),
            "severity": {
                "zone": severity.zone.value,
                "label": severity.label,
                "recommendation": severity.recommendation,
                "action_window": severity.action_window,
                "color": severity.color_hex,
            },
            "report_generated": report_path.exists(),
            "email_sent": email_sent,
            "annotated_image_base64": f"data:image/jpeg;base64,{image_b64}",
        }
    )


@bp.route("/reports/<path:filename>")
def download_report(filename):
    return send_from_directory(current_app.config["REPORT_OUTPUT_DIR"], filename, as_attachment=True)


@bp.route("/api/health")
def health():
    return jsonify({"status": "ok", "simulation_mode": current_app.config["SIMULATION_MODE"]})

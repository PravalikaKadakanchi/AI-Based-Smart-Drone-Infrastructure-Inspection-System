"""
Generates a professional PDF inspection report for each completed
inspection: date, GPS location, captured/annotated image, damage
classification, and recommendations.
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, HexColor as _HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from drone.telemetry import TelemetrySnapshot
from vision.crack_detector import CrackDetectionResult
from vision.severity_classifier import SeverityAssessment


PAGE_W, PAGE_H = A4
MARGIN = 20 * mm


def generate_report(
    output_path: Path,
    inspection_id: str,
    image_path: Path,
    telemetry: TelemetrySnapshot,
    crack_result: CrackDetectionResult,
    severity: SeverityAssessment,
    inspector_name: str = "Automated Inspection System",
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=A4)

    y = PAGE_H - MARGIN

    def line(text, size=11, bold=False, color=black, gap=7 * mm):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.setFillColor(color)
        c.drawString(MARGIN, y, text)
        y -= gap

    # Header
    line("Aero Vaani | Infrastructure Inspection Report", size=16, bold=True, gap=8 * mm)
    c.setStrokeColor(HexColor("#c8c8c8"))
    c.line(MARGIN, y, PAGE_W - MARGIN, y)
    y -= 8 * mm

    timestamp = datetime.fromtimestamp(telemetry.timestamp).strftime("%Y-%m-%d %H:%M:%S")
    line(f"Inspection ID: {inspection_id}")
    line(f"Date / Time: {timestamp}")
    line(f"Inspector: {inspector_name}", gap=10 * mm)

    line("GPS & Flight Data", size=12, bold=True)
    line(f"Latitude: {telemetry.latitude:.6f}")
    line(f"Longitude: {telemetry.longitude:.6f}")
    line(f"Altitude: {telemetry.altitude_m} m")
    line(f"Battery: {telemetry.battery_percent}%", gap=10 * mm)

    if image_path and Path(image_path).exists():
        line("Captured Image", size=12, bold=True, gap=6 * mm)
        try:
            img = ImageReader(str(image_path))
            iw, ih = img.getSize()
            display_w = 100 * mm
            display_h = display_w * ih / iw
            if y - display_h < MARGIN:
                display_h = y - MARGIN
                display_w = display_h * iw / ih
            c.drawImage(img, MARGIN, y - display_h, width=display_w, height=display_h)
            y -= display_h + 8 * mm
        except Exception:
            line("(image could not be embedded)", size=9)

    line("Damage Assessment", size=12, bold=True)
    line(f"Cracks Detected: {'Yes' if crack_result.crack_detected else 'No'}")
    line(f"Crack Count: {crack_result.crack_count}")
    line(f"Surface Coverage: {crack_result.coverage_ratio * 100:.2f}%", gap=9 * mm)

    line(
        f"Severity: {severity.zone.value} ZONE - {severity.label}",
        size=13,
        bold=True,
        color=_HexColor(severity.color_hex),
    )
    line(f"Recommendation: {severity.recommendation}")
    line(f"Action Window: {severity.action_window}")

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(HexColor("#787878"))
    c.drawCentredString(PAGE_W / 2, 10 * mm, "Generated automatically by AI Drone Inspection System")

    c.save()
    return output_path

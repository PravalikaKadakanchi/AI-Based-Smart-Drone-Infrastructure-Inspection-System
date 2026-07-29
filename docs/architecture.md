# Architecture Notes

## Overview

Aero Vaani is split into five independent, testable layers. Each layer
has a clean interface so hardware components (camera, Pixhawk) can be
swapped for simulated equivalents without touching the rest of the
pipeline — this is what allows the whole system to run and be
demonstrated on a laptop with no physical drone attached.

## Layers

### 1. `drone/` — Hardware Abstraction
- `camera.py`: wraps Picamera2. Falls back to generating synthetic
  inspection-style frames when no camera/`picamera2` is available.
- `telemetry.py`: wraps `pymavlink` for GPS/flight data from the
  Pixhawk. Falls back to simulated GPS jitter and flight telemetry
  when no flight controller is connected.

### 2. `vision/` — Computer Vision Pipeline
- `crack_detector.py`: classical OpenCV pipeline — Gaussian blur →
  Canny edge detection → morphological dilation → contour analysis.
  Contours are filtered by arc length and a rotation-aware aspect
  ratio (via `cv2.minAreaRect`) to distinguish long thin crack-like
  shapes from blob-like noise, regardless of the crack's orientation
  in the frame.
- `severity_classifier.py`: maps the crack coverage ratio to one of
  three severity zones (Green / Yellow / Red) with tunable thresholds.

### 3. `reports/` — Report Generation
- `pdf_generator.py`: builds a single-page PDF report (ReportLab) with
  inspection metadata, the annotated capture, and the severity
  assessment.

### 4. `notifications/` — Delivery
- `email_sender.py`: sends the generated PDF via SMTP. No-ops safely
  (with a log warning) if credentials aren't configured, so the rest
  of the pipeline still completes during development/demos.

### 5. `app/` — Presentation & Orchestration
- `routes.py` wires the above layers together behind a single
  `/api/inspect` endpoint that the dashboard calls.
- `templates/` + `static/` implement the live dashboard.

## Simulation Mode

Set via `SIMULATION_MODE` in `.env`. When `True` (the default):
- `DroneCamera` generates synthetic inspection frames with a randomly
  drawn "crack" line so the detection pipeline has something realistic
  to find.
- `TelemetryReader` generates plausible GPS coordinates (centered near
  a fixed reference point) and flight telemetry.

This lets contributors, recruiters, and CI pipelines run the full
system without any physical hardware.

## Extension Points

- Swap `CrackDetector` for a deep-learning-based detector by
  implementing the same `.detect(image) -> CrackDetectionResult`
  interface — no other layer needs to change.
- Swap `SeverityClassifier` thresholds/logic similarly by preserving
  the `.classify(result) -> SeverityAssessment` interface.

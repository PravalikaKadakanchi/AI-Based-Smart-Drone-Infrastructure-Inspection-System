# 🛰️ Aero Vaani — AI-Based Smart Drone Infrastructure Inspection System

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=for-the-badge&logo=OpenCV&logoColor=white)
![Raspberry Pi](https://img.shields.io/badge/Raspberry_Pi-C51A4A?style=for-the-badge&logo=raspberry-pi&logoColor=white)
![MIT License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**🏆 Winner — Hacksavvy-26 | 24-Hour National Hackathon | MGIT**

*Built by Team Aero Vaani — CMR College of Engineering & Technology (CMRCET), Hyderabad*

[🚀 Run Locally](#-installation) · [📖 Architecture](#-architecture) · [🧪 Tests](#-running-tests) · [🔮 Roadmap](#-future-improvements)

</div>

---

## 📌 What Is Aero Vaani?

An **autonomous drone-based inspection system** that flies to critical infrastructure (transmission towers, electric poles, bridges), captures live imagery, detects structural cracks using computer vision, tags findings with GPS coordinates, classifies damage severity into three action zones, and automatically generates and emails a professional PDF inspection report — **without a human ever having to climb the structure.**

---

## 📌 Problem Statement

Manual inspection of infrastructure is:

| Problem | Impact |
|---------|--------|
| ⏱️ Time-consuming | Each structure requires a physical visit |
| 💸 Expensive | Specialized equipment + trained personnel |
| ⚠️ Risky | Inspectors work at height / near live equipment |
| 📋 Inconsistent | Assessments vary; rarely GPS-logged |

**Aero Vaani** automates this entire workflow — from flight to inbox.

---

## ✨ Features

- 📷 **Live image capture** from Raspberry Pi Camera Module during flight
- 📍 **GPS & flight telemetry** from Pixhawk flight controller via MAVLink
- 🧠 **AI/CV crack detection** — OpenCV edge + contour pipeline optimized for Raspberry Pi
- 🟢🟡🔴 **Three-tier severity classification**:

  | Zone | Label | Action Window |
  |------|-------|--------------|
  | 🟢 Green | Minor Damage | Inspect within 7 days |
  | 🟡 Yellow | Moderate Damage | Maintenance within 3 days |
  | 🔴 Red | Critical Damage | Immediate action within 24 hours |

- 📊 **Live web dashboard** — real-time image, GPS, telemetry, classification
- 📄 **Auto PDF report** — GPS-tagged, severity-classified, with annotated image
- 📧 **Automated email delivery** of report to registered recipients
- 🧪 **Simulation mode** — full pipeline runs on a laptop with zero hardware

---

## 🏗️ Architecture

```
                    ┌────────────────────┐
                    │   Pixhawk Flight   │
                    │    Controller      │──── GPS + Telemetry (MAVLink)
                    └─────────┬──────────┘
                              │
   ┌──────────────────┐      │      ┌──────────────────────┐
   │  Raspberry Pi    │◄─────┘      │  Raspberry Pi Camera  │
   │ (onboard compute)│◄────────────│      Module           │
   └─────────┬────────┘             └──────────────────────┘
             │  captured frame + telemetry
             ▼
   ┌──────────────────────────┐
   │  Computer Vision Engine  │   OpenCV: Gaussian blur → Canny
   │  vision/crack_detector   │   → morphological filter → contours
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐
   │   Severity Classifier    │   Green / Yellow / Red zone logic
   └─────────────┬────────────┘
                 ▼
   ┌──────────────────────────┐        ┌─────────────────────────┐
   │   PDF Report Generator   │───────►│   Email Automation      │
   └─────────────┬────────────┘        └─────────────────────────┘
                 ▼
   ┌──────────────────────────┐
   │   Flask Web Dashboard    │   Live view of every inspection
   └──────────────────────────┘
```

**Data flow:** Drone flies → Pi Camera captures frame → Pixhawk supplies GPS via MAVLink → OpenCV detects cracks → Severity classifier assigns zone → PDF report generated → Report emailed → Results pushed to live dashboard.

---

## 📁 Project Structure

```
aero-vaani-drone-inspection/
├── run.py                        # 🚀 App entrypoint
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template (no secrets)
├── app/                          # Flask application
│   ├── __init__.py               #   App factory
│   ├── config.py                 #   Environment-based config
│   ├── routes.py                 #   Inspection pipeline API
│   ├── static/css/style.css      #   Dashboard styles
│   └── templates/                #   Jinja2 HTML templates
│       ├── base.html
│       └── dashboard.html
├── drone/                        # 🚁 Hardware interfaces
│   ├── camera.py                 #   Picamera2 wrapper + simulation
│   └── telemetry.py              #   MAVLink/Pixhawk + simulation
├── vision/                       # 🧠 Computer vision
│   ├── crack_detector.py         #   OpenCV crack detection
│   └── severity_classifier.py   #   Green/Yellow/Red classifier
├── reports/                      # 📄 PDF generation
│   └── pdf_generator.py
├── notifications/                # 📧 Email automation
│   └── email_sender.py
├── tests/                        # 🧪 Unit tests
│   ├── test_crack_detector.py
│   └── test_severity_classifier.py
├── data/
│   ├── sample_images/            # Sample inspection images
│   └── inspection_logs/          # Generated PDFs & captures
└── docs/
    ├── architecture.md
    └── screenshots/              # ← Hackathon photos go here
```

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- *(For real hardware)* Raspberry Pi + Camera Module + Pixhawk

### Quick Start (Simulation Mode — no hardware needed)

```bash
# 1. Clone
git clone https://github.com/PravalikaKadakanchi/AI-Based-Smart-Drone-Infrastructure-Inspection-System.git
cd AI-Based-Smart-Drone-Infrastructure-Inspection-System

# 2. Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure (simulation mode is ON by default)
cp .env.example .env

# 5. Run
python run.py
```

Open **http://localhost:5000** and click **"Run Inspection"** 🚁

> `SIMULATION_MODE=True` by default — synthetic camera frames + GPS telemetry generated automatically. No drone required!

### Real Hardware Mode (Raspberry Pi + Pixhawk)

```bash
# In your .env file:
SIMULATION_MODE=False
MAVLINK_CONNECTION=/dev/serial0   # or udp:127.0.0.1:14550
MAVLINK_BAUDRATE=57600

# SMTP for email reports
SMTP_USERNAME=your@email.com
SMTP_PASSWORD=your-app-password
REPORT_RECIPIENT_EMAIL=inspector@company.com
```

---

## 🖥️ Running in GitHub Codespaces (Zero Install!)

1. Click the green **"Code"** button on this repo
2. Select **"Codespaces"** → **"Create codespace on main"**
3. Wait ~1 minute for setup
4. In the terminal: `pip install -r requirements.txt && python run.py`
5. Click **"Open in Browser"** → Dashboard opens! ✅

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

```
tests/test_crack_detector.py     ✓ 4 tests
tests/test_severity_classifier.py ✓ 3 tests
```

---

## 📸 Screenshots & Demo

> *(Hackathon photos will be added here — see [docs/screenshots/](docs/screenshots/))*

| Dashboard | Inspection Result | PDF Report |
|-----------|-------------------|------------|
| *Coming soon* | *Coming soon* | *Coming soon* |

---

## 🧗 Engineering Challenges Solved in 24 Hours

- MAVLink communication reliability between Raspberry Pi and Pixhawk
- Raspberry Pi camera memory constraints during continuous capture
- GPS synchronization with image capture timing
- Real-time telemetry integration into the Flask dashboard
- OpenCV pipeline optimization for near-real-time crack detection on Pi hardware
- Reducing false positives using rotation-aware bounding boxes (minAreaRect)
- End-to-end PDF generation + email automation pipeline
- Hardware–software integration under 24-hour hackathon constraints

---

## 🔮 Future Improvements

- [ ] Replace classical CV with a trained deep-learning segmentation model (U-Net / YOLO-based)
- [ ] Autonomous flight path planning around structures
- [ ] Historical inspection dashboard with trend analysis per structure
- [ ] Multi-drone fleet support
- [ ] Offline-first mobile companion app for field engineers
- [ ] Role-based access control and multi-user report distribution
- [ ] GIS platform integration for asset-level tracking
- [ ] Real-time video streaming from drone camera

---

## 🛠️ Technologies Used

| Layer | Technology |
|-------|-----------|
| Onboard compute | Raspberry Pi 3 Model B+ |
| Camera | Raspberry Pi Camera Module + Picamera2 |
| Flight controller | Pixhawk (GPS + MAVLink telemetry) |
| Backend | Python 3 + Flask |
| Computer vision | OpenCV |
| Telemetry protocol | MAVLink via pymavlink |
| PDF reports | ReportLab |
| Email | smtplib (SMTP) |
| Frontend | HTML + CSS + JavaScript |
| Testing | pytest |

---

## 👥 Team Aero Vaani

**Pravalika Kadakanchi** — [GitHub](https://github.com/PravalikaKadakanchi)

*Representing CMR College of Engineering & Technology (CMRCET), Hyderabad*

🏆 **Winner — Hacksavvy-26 | 24-Hour National Hackathon | MGIT**

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

# Contributing to Aero Vaani

Thanks for your interest in improving this project! Contributions, bug
reports, and feature suggestions are all welcome.

## Getting Started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`. The default `SIMULATION_MODE=True`
   lets you run and test the full pipeline without any drone hardware.
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

- Keep hardware-dependent code (camera, MAVLink) behind the existing
  simulation-mode fallbacks so contributors without hardware can still
  run and test the project.
- Write or update tests in `tests/` for any change to `vision/`.
- Follow PEP 8; run `python -m py_compile` (or a formatter like `black`)
  before submitting.
- Never commit `.env`, credentials, captured images, or generated reports.

## Submitting Changes

1. Run the test suite and confirm everything passes.
2. Commit with a clear, descriptive message (e.g. `fix: correct crack aspect-ratio check for diagonal cracks`).
3. Push to your fork and open a Pull Request describing the change and motivation.

## Reporting Issues

Please include steps to reproduce, expected vs. actual behavior, and
whether you were running in simulation mode or on real hardware.

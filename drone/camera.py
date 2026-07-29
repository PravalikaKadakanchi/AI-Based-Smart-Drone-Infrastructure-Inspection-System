"""
Camera interface for the Raspberry Pi Camera Module.

On real hardware this wraps Picamera2. When SIMULATION_MODE is enabled
(or Picamera2 / the camera hardware isn't available, e.g. during
development on a laptop), it falls back to generating synthetic
inspection frames so the rest of the pipeline can run end-to-end.
"""

import time
import logging
from pathlib import Path

import numpy as np
import cv2

logger = logging.getLogger(__name__)

try:
    from picamera2 import Picamera2  # type: ignore

    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False


class DroneCamera:
    """Unified camera interface with automatic hardware/simulation fallback."""

    def __init__(self, simulation_mode: bool = True, resolution=(1280, 720)):
        self.resolution = resolution
        self.simulation_mode = simulation_mode or not PICAMERA_AVAILABLE
        self._picam = None

        if not self.simulation_mode:
            self._picam = Picamera2()
            config = self._picam.create_still_configuration(
                main={"size": resolution}
            )
            self._picam.configure(config)
            self._picam.start()
            time.sleep(1)  # allow sensor to warm up
            logger.info("Raspberry Pi camera initialized.")
        else:
            logger.info("Camera running in SIMULATION mode (no hardware attached).")

    def capture_frame(self) -> np.ndarray:
        """Capture a single BGR frame as a numpy array."""
        if self.simulation_mode:
            return self._generate_synthetic_frame()

        frame = self._picam.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def capture_to_file(self, output_path: Path) -> Path:
        frame = self.capture_frame()
        cv2.imwrite(str(output_path), frame)
        return output_path

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Generate a plausible infrastructure-inspection style test frame."""
        w, h = self.resolution
        frame = np.full((h, w, 3), (120, 120, 130), dtype=np.uint8)  # concrete-grey base

        # Add subtle texture/noise
        noise = np.random.randint(-15, 15, (h, w, 3), dtype=np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

        # Randomly draw a "crack" line to simulate a structural defect
        if np.random.rand() > 0.4:
            pt1 = (np.random.randint(0, w), np.random.randint(0, h))
            pt2 = (
                pt1[0] + np.random.randint(-200, 200),
                pt1[1] + np.random.randint(-200, 200),
            )
            cv2.line(frame, pt1, pt2, (40, 40, 40), thickness=np.random.randint(1, 4))

        return frame

    def close(self):
        if not self.simulation_mode and self._picam is not None:
            self._picam.stop()

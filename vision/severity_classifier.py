"""
Damage severity classification.

Maps raw crack-detection metrics into the three-tier action zones used
throughout the system: Green (minor), Yellow (moderate), Red (critical).
"""

from dataclasses import dataclass
from enum import Enum

from vision.crack_detector import CrackDetectionResult


class SeverityZone(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


@dataclass
class SeverityAssessment:
    zone: SeverityZone
    label: str
    recommendation: str
    action_window: str
    color_hex: str


_ZONE_META = {
    SeverityZone.GREEN: dict(
        label="Minor Damage",
        recommendation="Routine inspection recommended.",
        action_window="Within 7 days",
        color_hex="#22c55e",
    ),
    SeverityZone.YELLOW: dict(
        label="Moderate Damage",
        recommendation="Maintenance required.",
        action_window="Within 3 days",
        color_hex="#eab308",
    ),
    SeverityZone.RED: dict(
        label="Critical Damage",
        recommendation="Immediate action required.",
        action_window="Within 24 hours",
        color_hex="#ef4444",
    ),
}


class SeverityClassifier:
    """
    Thresholds are tunable via config and were calibrated against the
    demo dataset used during the hackathon. Swap in a trained
    classifier here as the model matures (see README > Future Improvements).
    """

    def __init__(self, yellow_threshold: float = 0.015, red_threshold: float = 0.045):
        self.yellow_threshold = yellow_threshold
        self.red_threshold = red_threshold

    def classify(self, result: CrackDetectionResult) -> SeverityAssessment:
        if not result.crack_detected or result.coverage_ratio < self.yellow_threshold:
            zone = SeverityZone.GREEN
        elif result.coverage_ratio < self.red_threshold:
            zone = SeverityZone.YELLOW
        else:
            zone = SeverityZone.RED

        meta = _ZONE_META[zone]
        return SeverityAssessment(zone=zone, **meta)

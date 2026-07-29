import numpy as np

from vision.crack_detector import CrackDetectionResult
from vision.severity_classifier import SeverityClassifier, SeverityZone


def _fake_result(coverage_ratio, crack_detected=True):
    return CrackDetectionResult(
        crack_detected=crack_detected,
        crack_count=1 if crack_detected else 0,
        total_crack_length_px=100.0,
        coverage_ratio=coverage_ratio,
        annotated_image=np.zeros((10, 10, 3), dtype=np.uint8),
    )


def test_green_zone_for_no_cracks():
    classifier = SeverityClassifier()
    result = _fake_result(coverage_ratio=0.0, crack_detected=False)
    assessment = classifier.classify(result)
    assert assessment.zone == SeverityZone.GREEN


def test_yellow_zone_for_moderate_coverage():
    classifier = SeverityClassifier(yellow_threshold=0.01, red_threshold=0.05)
    result = _fake_result(coverage_ratio=0.02)
    assessment = classifier.classify(result)
    assert assessment.zone == SeverityZone.YELLOW


def test_red_zone_for_high_coverage():
    classifier = SeverityClassifier(yellow_threshold=0.01, red_threshold=0.05)
    result = _fake_result(coverage_ratio=0.1)
    assessment = classifier.classify(result)
    assert assessment.zone == SeverityZone.RED

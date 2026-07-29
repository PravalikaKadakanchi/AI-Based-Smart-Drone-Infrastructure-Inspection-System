import numpy as np
import cv2

from vision.crack_detector import CrackDetector


def test_blank_image_has_no_cracks():
    detector = CrackDetector()
    blank = np.full((300, 300, 3), 120, dtype=np.uint8)
    result = detector.detect(blank)
    assert result.crack_detected is False
    assert result.crack_count == 0


def test_synthetic_line_is_detected_as_crack():
    detector = CrackDetector(min_contour_length=20)
    image = np.full((300, 300, 3), 120, dtype=np.uint8)
    cv2.line(image, (20, 20), (280, 280), (10, 10, 10), thickness=2)

    result = detector.detect(image)
    assert result.crack_detected is True
    assert result.crack_count >= 1
    assert result.coverage_ratio > 0

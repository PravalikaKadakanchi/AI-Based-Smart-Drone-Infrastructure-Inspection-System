"""
Crack / structural-defect detection using classical computer vision.

This module uses an OpenCV edge-and-contour based pipeline (Gaussian
blur -> adaptive threshold -> Canny -> morphological filtering ->
contour analysis) to flag likely crack regions on infrastructure
surfaces such as poles, towers, and bridge segments.

Note: this is a lightweight, dependency-free CV baseline suitable for
running on a Raspberry Pi in real time. A trained deep-learning model
(e.g. a fine-tuned segmentation network) is a natural upgrade path —
see "Future Improvements" in the README.
"""

from dataclasses import dataclass, field
from typing import List, Tuple

import cv2
import numpy as np


@dataclass
class CrackDetectionResult:
    crack_detected: bool
    crack_count: int
    total_crack_length_px: float
    coverage_ratio: float  # fraction of image area flagged as crack-like
    annotated_image: np.ndarray
    bounding_boxes: List[Tuple[int, int, int, int]] = field(default_factory=list)


class CrackDetector:
    def __init__(self, min_contour_length: int = 40, canny_low: int = 50, canny_high: int = 150):
        self.min_contour_length = min_contour_length
        self.canny_low = canny_low
        self.canny_high = canny_high

    def detect(self, image: np.ndarray) -> CrackDetectionResult:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blurred, self.canny_low, self.canny_high)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        annotated = image.copy()
        crack_contours = []
        boxes = []
        total_length = 0.0
        crack_pixel_area = 0

        for c in contours:
            length = cv2.arcLength(c, closed=False)
            x, y, w, h = cv2.boundingRect(c)

            # Use a rotation-aware bounding box (minAreaRect) rather than the
            # axis-aligned box, since axis-aligned width/height are equal for
            # a diagonal crack (e.g. a 45-degree line) and would wrongly fail
            # a simple w/h aspect-ratio check.
            if len(c) >= 5:
                (_, _), (rect_w, rect_h), _ = cv2.minAreaRect(c)
                aspect_ratio = max(rect_w, rect_h) / max(min(rect_w, rect_h), 1e-3)
            else:
                aspect_ratio = max(w, h) / max(min(w, h), 1)

            # Cracks tend to be long, thin, irregular shapes rather than blobs.
            if length >= self.min_contour_length and aspect_ratio >= 2.5:
                crack_contours.append(c)
                boxes.append((x, y, w, h))
                total_length += length
                crack_pixel_area += cv2.contourArea(c)
                cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.drawContours(annotated, [c], -1, (0, 255, 255), 1)

        image_area = image.shape[0] * image.shape[1]
        coverage_ratio = crack_pixel_area / image_area if image_area else 0.0

        return CrackDetectionResult(
            crack_detected=len(crack_contours) > 0,
            crack_count=len(crack_contours),
            total_crack_length_px=total_length,
            coverage_ratio=coverage_ratio,
            annotated_image=annotated,
            bounding_boxes=boxes,
        )

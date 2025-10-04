"""Base detector class with shared functionality"""
import cv2
from utils.image_processor import capture_screenshot, create_hsv_mask, apply_morphology, save_debug_image
from utils.geometry import calculate_contour_properties, get_mean_hsv
from config import ScreenConfig, DebugConfig


class BaseDetector:
    """Base class for object detection"""

    def __init__(self, detection_config):
        """
        Initialize detector

        Args:
            detection_config: Configuration class with detection parameters
        """
        self.config = detection_config
        self.last_bgr_image = None
        self.last_hsv_image = None
        self.last_mask = None
        self.candidates = []
        self.rejected = []

    def _capture_and_process(self):
        """Capture screenshot and create HSV mask"""
        # Capture screenshot
        self.last_bgr_image, self.last_hsv_image = capture_screenshot(
            ScreenConfig.get_region()
        )

        # Create mask
        self.last_mask = create_hsv_mask(
            self.last_hsv_image,
            self.config.LOWER_HSV,
            self.config.UPPER_HSV
        )

    def _apply_morphology(self, operations):
        """Apply morphological operations to mask"""
        self.last_mask = apply_morphology(self.last_mask, operations)

    def _find_contours(self):
        """Find contours in mask"""
        contours, _ = cv2.findContours(
            self.last_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours

    def _analyze_contour(self, contour):
        """
        Analyze single contour and extract all properties

        Args:
            contour: OpenCV contour

        Returns:
            dict with geometric and color properties
        """
        # Get geometric properties
        props = calculate_contour_properties(contour)

        # Get color properties
        color_props = get_mean_hsv(self.last_hsv_image, contour)

        # Merge properties
        return {**props, **color_props}

    def _filter_candidates(self, contours, filter_fn):
        """
        Filter contours based on criteria

        Args:
            contours: list of OpenCV contours
            filter_fn: function that takes properties dict and returns (is_valid, reason)

        Returns:
            tuple of (candidates, rejected)
        """
        candidates = []
        rejected = []

        for contour in contours:
            props = self._analyze_contour(contour)
            is_valid, reason = filter_fn(props)

            if is_valid:
                candidates.append(props)
            else:
                props['reason'] = reason
                rejected.append(props)

        return candidates, rejected

    def _save_debug_images(self, original_filename, mask_filename, detected_filename):
        """Save debug images if debugging is enabled"""
        if not DebugConfig.ENABLED:
            return

        save_debug_image(self.last_bgr_image, original_filename)
        save_debug_image(self.last_mask, mask_filename)

    def _get_best_candidate(self, sort_key='area'):
        """
        Get best candidate from list

        Args:
            sort_key: key to sort by (default: 'area')

        Returns:
            Best candidate or None
        """
        if not self.candidates:
            return None

        # Sort by specified key (largest first)
        self.candidates.sort(key=lambda x: x[sort_key], reverse=True)
        return self.candidates[0]

    def detect(self):
        """
        Detect object - to be implemented by subclasses

        Returns:
            tuple of (type, x, y) or None
        """
        raise NotImplementedError("Subclasses must implement detect()")

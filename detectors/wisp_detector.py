"""Wisp detection using blob detection"""
from detectors.base import BaseDetector
from utils.image_processor import draw_detections, draw_rejected_objects, save_debug_image
from config import WispDetectionConfig, ScreenConfig, DebugConfig


class WispDetector(BaseDetector):
    """Detector for wisps using blob detection"""

    def __init__(self):
        super().__init__(WispDetectionConfig)

    def _filter_wisp(self, props):
        """
        Filter function for wisp candidates

        Args:
            props: dict with contour properties

        Returns:
            tuple of (is_valid, reason)
        """
        area = props['area']
        circularity = props['circularity']
        aspect_ratio = props['aspect_ratio']

        # Check if properties match wisp characteristics
        if not (WispDetectionConfig.MIN_AREA < area < WispDetectionConfig.MAX_AREA):
            return False, f"A:{int(area)} C:{circularity:.2f}"

        if circularity <= WispDetectionConfig.MIN_CIRCULARITY:
            return False, f"A:{int(area)} C:{circularity:.2f}"

        if not (WispDetectionConfig.MIN_ASPECT_RATIO < aspect_ratio < WispDetectionConfig.MAX_ASPECT_RATIO):
            return False, f"A:{int(area)} C:{circularity:.2f}"

        return True, ""

    def _create_debug_visualization(self):
        """Create debug visualization with detected and rejected wisps"""
        if not DebugConfig.ENABLED:
            return

        debug_image = self.last_bgr_image.copy()

        # Draw rejected objects in red
        debug_image = draw_rejected_objects(
            debug_image,
            self.rejected,
            (0, 0, 255),
            lambda obj: obj['reason']
        )

        # Draw wisp candidates in green
        debug_image = draw_detections(
            debug_image,
            self.candidates,
            (0, 255, 0),
            lambda obj, i: f"W{i+1} A:{int(obj['area'])} C:{obj['circularity']:.2f} H:{int(obj['hue'])}"
        )

        save_debug_image(debug_image, DebugConfig.WISP_DETECTED)

    def detect(self):
        """
        Detect wisps in screenshot

        Returns:
            tuple of ('wisp', screen_x, screen_y) or None
        """
        # Capture and process image
        self._capture_and_process()

        # Apply morphological operations
        self._apply_morphology([
            ('open', WispDetectionConfig.MORPH_KERNEL_SIZE),
            ('close', WispDetectionConfig.MORPH_KERNEL_SIZE)
        ])

        # Save debug images
        self._save_debug_images(
            DebugConfig.WISP_ORIGINAL,
            DebugConfig.WISP_MASK,
            DebugConfig.WISP_DETECTED
        )

        # Find contours
        contours = self._find_contours()

        # Filter candidates
        self.candidates, self.rejected = self._filter_candidates(contours, self._filter_wisp)

        # Create debug visualization
        self._create_debug_visualization()

        # Get best candidate
        best_wisp = self._get_best_candidate('area')

        if best_wisp:
            # Convert to screen coordinates
            screen_x, screen_y = ScreenConfig.to_screen_coords(
                best_wisp['center'][0],
                best_wisp['center'][1]
            )

            print(f"Wisp found at screen coordinates: ({screen_x}, {screen_y})")
            print(f"Area: {best_wisp['area']}, Circularity: {best_wisp['circularity']:.2f}, Hue: {best_wisp['hue']:.1f}")

            return ('wisp', screen_x, screen_y)

        print("No wisps detected")
        return None

"""Energy rift detection"""
from detectors.base import BaseDetector
from utils.image_processor import draw_detections, save_debug_image
from config import RiftDetectionConfig, ScreenConfig, DebugConfig
import cv2


class RiftDetector(BaseDetector):
    """Detector for energy rifts"""

    def __init__(self):
        super().__init__(RiftDetectionConfig)

    def _filter_rift(self, props):
        """
        Filter function for rift candidates

        Args:
            props: dict with contour properties

        Returns:
            tuple of (is_valid, reason)
        """
        area = props['area']
        value = props['value']
        saturation = props['saturation']

        # Check if properties match rift characteristics
        if area <= RiftDetectionConfig.MIN_AREA:
            return False, f"A:{int(area)} V:{int(value)}"

        if value <= RiftDetectionConfig.MIN_VALUE:
            return False, f"A:{int(area)} V:{int(value)}"

        if saturation <= RiftDetectionConfig.MIN_SATURATION:
            return False, f"A:{int(area)} V:{int(value)}"

        return True, ""

    def _create_debug_visualization(self):
        """Create debug visualization with detected and rejected rifts"""
        if not DebugConfig.ENABLED:
            return

        debug_image = self.last_bgr_image.copy()

        # Draw rejected candidates in blue
        for obj in self.rejected:
            cv2.circle(debug_image, obj['center'], 5, (255, 0, 0), 2)
            cv2.putText(debug_image, obj['reason'], (obj['center'][0], obj['center'][1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        # Draw rift candidates in red
        debug_image = draw_detections(
            debug_image,
            self.candidates,
            (0, 0, 255),
            lambda obj, i: f"RIFT A:{int(obj['area'])} H:{int(obj['hue'])} V:{int(obj['value'])}"
        )

        # Use thicker lines for rifts
        for candidate in self.candidates:
            cv2.drawContours(debug_image, [candidate['contour']], -1, (0, 0, 255), 3)

        save_debug_image(debug_image, DebugConfig.RIFT_DETECTED)

    def detect(self):
        """
        Detect energy rift in screenshot

        Returns:
            tuple of ('rift', screen_x, screen_y) or None
        """
        # Capture and process image
        self._capture_and_process()

        # Apply morphological operations
        self._apply_morphology([
            ('close', RiftDetectionConfig.CLOSE_KERNEL_SIZE),
            ('open', RiftDetectionConfig.OPEN_KERNEL_SIZE)
        ])

        # Save debug images
        self._save_debug_images(
            DebugConfig.RIFT_ORIGINAL,
            DebugConfig.RIFT_MASK,
            DebugConfig.RIFT_DETECTED
        )

        # Find contours
        contours = self._find_contours()

        # Filter candidates
        self.candidates, self.rejected = self._filter_candidates(contours, self._filter_rift)

        # Create debug visualization
        self._create_debug_visualization()

        # Get best candidate (largest area)
        best_rift = self._get_best_candidate('area')

        if best_rift:
            # Convert to screen coordinates
            screen_x, screen_y = ScreenConfig.to_screen_coords(
                best_rift['center'][0],
                best_rift['center'][1]
            )

            print(f"Energy rift found at: ({screen_x}, {screen_y})")
            print(f"  Area: {best_rift['area']}, Hue: {best_rift['hue']:.1f}, Value: {best_rift['value']:.1f}, Sat: {best_rift['saturation']:.1f}")

            return ('rift', screen_x, screen_y)

        print("Energy rift not found")
        print(f"  Rejected {len(self.rejected)} candidates (too small or too dark)")
        return None

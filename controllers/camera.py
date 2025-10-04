"""Camera control"""
import pyautogui
import time
import random
from config import CameraConfig


class CameraController:
    """Handles camera rotation"""

    @staticmethod
    def rotate(direction=None, duration=None):
        """
        Rotate camera using arrow keys

        Args:
            direction: 'left' or 'right', or None for random
            duration: rotation duration in seconds, or None for random
        """
        # Use random direction if not specified
        if direction is None:
            direction = random.choice(CameraConfig.DIRECTIONS)

        # Use random duration if not specified
        if duration is None:
            duration = random.uniform(
                CameraConfig.MIN_ROTATION_DURATION,
                CameraConfig.MAX_ROTATION_DURATION
            )

        print(f"Rotating camera {direction} for {duration:.1f} seconds...")

        # Press and hold arrow key
        pyautogui.keyDown(direction)
        time.sleep(duration)
        pyautogui.keyUp(direction)

        # Small delay after rotation
        time.sleep(CameraConfig.DELAY_AFTER_ROTATION)

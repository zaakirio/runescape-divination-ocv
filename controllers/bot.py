"""Main bot controller"""
import pyautogui
import time
import random
from detectors.wisp_detector import WispDetector
from detectors.rift_detector import RiftDetector
from controllers.camera import CameraController
from config import BotConfig


class BotController:
    """Main bot orchestrator for Divination"""

    def __init__(self):
        self.wisp_detector = WispDetector()
        self.rift_detector = RiftDetector()
        self.camera = CameraController()
        self.wisp_harvest_count = 0
        self.max_harvests_before_rift = BotConfig.INITIAL_HARVESTS_BEFORE_RIFT

    def _harvest_wisp(self, x, y):
        """
        Click and harvest a wisp

        Args:
            x: screen x coordinate
            y: screen y coordinate
        """
        # Random click duration 
        click_duration = random.uniform(
            BotConfig.MIN_CLICK_DURATION,
            BotConfig.MAX_CLICK_DURATION
        )
        print(f"Clicking wisp at ({x}, {y}) with {click_duration:.2f}s movement")

        pyautogui.moveTo(x, y, duration=click_duration)
        pyautogui.click()

        # Random harvest time
        harvest_time = random.uniform(
            BotConfig.MIN_HARVEST_TIME,
            BotConfig.MAX_HARVEST_TIME
        )
        print(f"Harvesting for {harvest_time:.1f} seconds...")

        time.sleep(harvest_time)

        self.wisp_harvest_count += 1
        print(f"Completed harvest #{self.wisp_harvest_count}")

    def _convert_at_rift(self, x, y):
        """
        Click and convert memories at energy rift

        Args:
            x: screen x coordinate
            y: screen y coordinate
        """
        # Random click duration
        click_duration = random.uniform(
            BotConfig.MIN_CLICK_DURATION,
            BotConfig.MAX_CLICK_DURATION
        )
        print(f"Clicking energy rift at ({x}, {y})")

        pyautogui.moveTo(x, y, duration=click_duration)
        pyautogui.click()

        # Random conversion time
        convert_time = random.uniform(
            BotConfig.MIN_CONVERT_TIME,
            BotConfig.MAX_CONVERT_TIME
        )
        print(f"Converting memories for {convert_time:.1f} seconds...")

        time.sleep(convert_time)

        # Reset counter for next cycle
        self.wisp_harvest_count = 0
        self.max_harvests_before_rift = BotConfig.SUBSEQUENT_HARVESTS_BEFORE_RIFT
        print(f"Next rift visit after {self.max_harvests_before_rift} harvest")

    def _handle_no_wisp(self):
        """Handle case when no wisp is found"""
        print("No wisps found, rotating camera...")
        self.camera.rotate()
        time.sleep(BotConfig.DELAY_WHEN_NO_WISP)

    def _handle_rift_search(self):
        """Search for and click energy rift with retries"""
        print(f"Time to convert at rift (after {self.wisp_harvest_count} harvests)")

        for attempt in range(BotConfig.MAX_RIFT_ATTEMPTS):
            print(f"Looking for energy rift (attempt {attempt + 1}/{BotConfig.MAX_RIFT_ATTEMPTS})...")
            rift_result = self.rift_detector.detect()

            if rift_result:
                _, rift_x, rift_y = rift_result
                self._convert_at_rift(rift_x, rift_y)
                return True
            else:
                print("Energy rift not found, rotating camera...")
                self.camera.rotate()
                time.sleep(BotConfig.DELAY_AFTER_ROTATION)

        print(f"WARNING: Could not find energy rift after {BotConfig.MAX_RIFT_ATTEMPTS} attempts!")
        print("Continuing with wisp harvesting...")
        return False

    def run(self):
        """Main bot loop"""
        print("Starting Divination bot...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                # Look for wisps
                result = self.wisp_detector.detect()

                if result and result[0] == 'wisp':
                    _, x, y = result
                    self._harvest_wisp(x, y)

                    # Check if it's time to convert at rift
                    if self.wisp_harvest_count >= self.max_harvests_before_rift:
                        self._handle_rift_search()
                else:
                    self._handle_no_wisp()

        except KeyboardInterrupt:
            print(f"\nBot stopped. Total harvests completed: {self.wisp_harvest_count}")

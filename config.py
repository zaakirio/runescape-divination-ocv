"""Configuration for Divination Bot"""

class ScreenConfig:
    """Screen capture and coordinate settings"""
    REGION_X = 5
    REGION_Y = 40
    REGION_WIDTH = 400
    REGION_HEIGHT = 700

    @classmethod
    def get_region(cls):
        return (cls.REGION_X, cls.REGION_Y, cls.REGION_WIDTH, cls.REGION_HEIGHT)

    @classmethod
    def to_screen_coords(cls, x, y):
        """Convert region coordinates to screen coordinates"""
        return x + cls.REGION_X, y + cls.REGION_Y


class WispDetectionConfig:
    """Configuration for wisp detection"""
    # HSV color ranges for cyan/blue-green wisps
    LOWER_HSV = (85, 50, 50)
    UPPER_HSV = (110, 255, 255)

    # Shape and size filters
    MIN_AREA = 50
    MAX_AREA = 1000
    MIN_CIRCULARITY = 0.3
    MIN_ASPECT_RATIO = 0.4
    MAX_ASPECT_RATIO = 2.5

    # Morphology kernel size
    MORPH_KERNEL_SIZE = (3, 3)


class RiftDetectionConfig:
    """Configuration for energy rift detection"""
    # HSV color ranges for bright lime-green/yellow-green rifts
    LOWER_HSV = (40, 120, 150)
    UPPER_HSV = (70, 255, 255)

    # Shape and size filters
    MIN_AREA = 3000
    MIN_VALUE = 150
    MIN_SATURATION = 100

    # Morphology kernel sizes
    CLOSE_KERNEL_SIZE = (15, 15)
    OPEN_KERNEL_SIZE = (5, 5)


class BotConfig:
    """Bot behavior configuration"""
    # Harvest timing (seconds)
    MIN_HARVEST_TIME = 20
    MAX_HARVEST_TIME = 30

    # Conversion timing (seconds)
    MIN_CONVERT_TIME = 30
    MAX_CONVERT_TIME = 40

    # Click movement duration (seconds)
    MIN_CLICK_DURATION = 0.3
    MAX_CLICK_DURATION = 0.7

    # Harvests before rift conversion
    INITIAL_HARVESTS_BEFORE_RIFT = 2
    SUBSEQUENT_HARVESTS_BEFORE_RIFT = 1

    # Rift search settings
    MAX_RIFT_ATTEMPTS = 10
    DELAY_AFTER_ROTATION = 1.0
    DELAY_WHEN_NO_WISP = 1.0


class CameraConfig:
    """Camera rotation configuration"""
    MIN_ROTATION_DURATION = 0.5
    MAX_ROTATION_DURATION = 1.5
    DELAY_AFTER_ROTATION = 0.5
    DIRECTIONS = ['left', 'right', 'up', 'down']


class DebugConfig:
    """Debug output configuration"""
    ENABLED = True
    DEBUG_DIR = 'debug-screenshots'

    # File names for debug output
    WISP_ORIGINAL = 'debug-screenshots/original.png'
    WISP_MASK = 'debug-screenshots/mask.png'
    WISP_DETECTED = 'debug-screenshots/detected_objects.png'

    RIFT_ORIGINAL = 'debug-screenshots/rift_original.png'
    RIFT_MASK = 'debug-screenshots/rift_mask.png'
    RIFT_DETECTED = 'debug-screenshots/rift_detected.png'

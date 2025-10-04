"""Image capture and processing utilities"""
import pyautogui
import cv2
import numpy as np


def capture_screenshot(region):
    """
    Capture screenshot and convert to OpenCV format

    Args:
        region: tuple of (x, y, width, height)

    Returns:
        tuple of (BGR image, HSV image)
    """
    # Take screenshot
    screenshot = pyautogui.screenshot(region=region)

    # Convert PIL image to OpenCV format
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Convert to HSV
    hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)

    return screenshot_bgr, hsv


def create_hsv_mask(hsv_image, lower_hsv, upper_hsv):
    """
    Create binary mask based on HSV range

    Args:
        hsv_image: HSV format image
        lower_hsv: tuple of (H, S, V) lower bounds
        upper_hsv: tuple of (H, S, V) upper bounds

    Returns:
        Binary mask
    """
    lower = np.array(lower_hsv)
    upper = np.array(upper_hsv)
    return cv2.inRange(hsv_image, lower, upper)


def apply_morphology(mask, operations):
    """
    Apply morphological operations to clean up mask

    Args:
        mask: Binary mask
        operations: list of tuples [(operation, kernel_size), ...]
                   operation can be 'open', 'close', 'erode', 'dilate'

    Returns:
        Cleaned mask
    """
    result = mask.copy()

    operation_map = {
        'open': cv2.MORPH_OPEN,
        'close': cv2.MORPH_CLOSE,
        'erode': cv2.MORPH_ERODE,
        'dilate': cv2.MORPH_DILATE
    }

    for operation, kernel_size in operations:
        kernel = np.ones(kernel_size, np.uint8)
        morph_op = operation_map.get(operation)
        if morph_op:
            result = cv2.morphologyEx(result, morph_op, kernel)

    return result


def save_debug_image(image, filename):
    """Save image for debugging"""
    cv2.imwrite(filename, image)


def draw_detections(image, objects, color, label_fn=None):
    """
    Draw detected objects on image

    Args:
        image: BGR image to draw on (will be modified)
        objects: list of detection objects with 'contour' and 'center' keys
        color: BGR color tuple
        label_fn: optional function that takes object and returns label string

    Returns:
        Annotated image
    """
    result = image.copy()

    for i, obj in enumerate(objects):
        # Draw contour
        cv2.drawContours(result, [obj['contour']], -1, color, 2)

        # Draw center point
        cv2.circle(result, obj['center'], 3, (255, 0, 0), -1)

        # Draw label if function provided
        if label_fn:
            label = label_fn(obj, i)
            cv2.putText(result, label, (obj['center'][0], obj['center'][1] + 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

    return result


def draw_rejected_objects(image, objects, color, label_fn=None):
    """
    Draw rejected objects on image (thinner lines, no center marker)

    Args:
        image: BGR image to draw on (will be modified)
        objects: list of rejected objects with 'contour' and 'center' keys
        color: BGR color tuple
        label_fn: optional function that takes object and returns label string

    Returns:
        Annotated image
    """
    result = image.copy()

    for obj in objects:
        # Draw contour with thin line
        cv2.drawContours(result, [obj['contour']], -1, color, 1)

        # Draw label if function provided
        if label_fn:
            label = label_fn(obj)
            cv2.putText(result, label, (obj['center'][0], obj['center'][1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)

    return result

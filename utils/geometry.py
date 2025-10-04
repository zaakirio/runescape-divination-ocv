"""Geometry and contour analysis utilities"""
import cv2
import numpy as np


def calculate_contour_properties(contour):
    """
    Calculate geometric properties of a contour

    Args:
        contour: OpenCV contour

    Returns:
        dict with area, circularity, aspect_ratio, center, bounding_box
    """
    area = cv2.contourArea(contour)

    # Get bounding box
    x, y, w, h = cv2.boundingRect(contour)

    # Calculate aspect ratio
    aspect_ratio = float(w) / h if h > 0 else 0

    # Calculate center point
    center_x = x + w // 2
    center_y = y + h // 2

    # Calculate circularity
    perimeter = cv2.arcLength(contour, True)
    circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

    return {
        'area': area,
        'circularity': circularity,
        'aspect_ratio': aspect_ratio,
        'center': (center_x, center_y),
        'bounding_box': (x, y, w, h),
        'contour': contour
    }


def get_mean_hsv(hsv_image, contour):
    """
    Calculate mean HSV values for pixels within a contour

    Args:
        hsv_image: HSV format image
        contour: OpenCV contour

    Returns:
        dict with hue, saturation, value
    """
    # Create mask for single contour
    mask = np.zeros(hsv_image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], -1, 255, -1)

    # Calculate mean HSV
    mean_hsv = cv2.mean(hsv_image, mask=mask)

    return {
        'hue': mean_hsv[0],
        'saturation': mean_hsv[1],
        'value': mean_hsv[2]
    }

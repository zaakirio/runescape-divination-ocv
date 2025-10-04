import pyautogui
import cv2
import numpy as np
import time
import random

def findWispWithBlobDetection(exclude_rift=True):
    """Find wisps using blob detection - more reliable than color matching"""

    # Take screenshot
    screenshot = pyautogui.screenshot(region=(300, 300, 400, 400))  # Adjust region as needed

    # Convert PIL image to OpenCV format
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Save original for debugging
    cv2.imwrite('original.png', screenshot_bgr)

    # Convert to HSV for better color filtering
    hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)

    # Define HSV ranges specifically for WISPS (cyan/blue-green color)
    # Wisps are distinctly blue-green/cyan (hue ~85-110), NOT yellow-green like rifts
    lower_wisp = np.array([85, 50, 50])  # Cyan/blue-green
    upper_wisp = np.array([110, 255, 255])

    # Create mask for wisp colors only
    mask = cv2.inRange(hsv, lower_wisp, upper_wisp)

    # Apply morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Remove noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fill gaps

    # Save mask for debugging
    cv2.imwrite('mask.png', mask)

    # Find contours (blobs)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and find wisp-like blobs
    wisp_candidates = []
    rejected_objects = []

    for contour in contours:
        area = cv2.contourArea(contour)

        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate aspect ratio
        aspect_ratio = float(w) / h

        # Calculate center point
        center_x = x + w // 2
        center_y = y + h // 2

        # Calculate circularity
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

        # Calculate mean HSV hue for this object
        mask_single = np.zeros(screenshot_bgr.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask_single, [contour], -1, 255, -1)
        mean_hsv = cv2.mean(hsv, mask=mask_single)
        mean_hue = mean_hsv[0]

        # Filtering for wisps - relaxed thresholds for better detection
        # Wisps: small area (50-1000), reasonably circular (>0.3), cyan color
        if 50 < area < 1000 and circularity > 0.3 and 0.4 < aspect_ratio < 2.5:
            wisp_candidates.append({
                'center': (center_x, center_y),
                'area': area,
                'circularity': circularity,
                'contour': contour,
                'hue': mean_hue
            })
        else:
            # Track rejected objects for debugging
            rejected_objects.append({
                'center': (center_x, center_y),
                'area': area,
                'circularity': circularity,
                'contour': contour,
                'hue': mean_hue,
                'reason': f"A:{int(area)} C:{circularity:.2f}"
            })

    # Debug visualization
    debug_image = screenshot_bgr.copy()

    # Draw rejected objects in red with reason
    for obj in rejected_objects:
        cv2.drawContours(debug_image, [obj['contour']], -1, (0, 0, 255), 1)
        cv2.putText(debug_image, obj['reason'], (obj['center'][0], obj['center'][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)

    # Draw wisps in green with detailed info
    for i, candidate in enumerate(wisp_candidates):
        cv2.drawContours(debug_image, [candidate['contour']], -1, (0, 255, 0), 2)
        cv2.circle(debug_image, candidate['center'], 3, (255, 0, 0), -1)
        label = f"W{i+1} A:{int(candidate['area'])} C:{candidate['circularity']:.2f} H:{int(candidate['hue'])}"
        cv2.putText(debug_image, label, (candidate['center'][0], candidate['center'][1] + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

    cv2.imwrite('detected_objects.png', debug_image)

    if wisp_candidates:
        # Sort by area (larger wisps might be closer/better targets)
        wisp_candidates.sort(key=lambda x: x['area'], reverse=True)

        # Get the best candidate
        best_wisp = wisp_candidates[0]

        # Convert to screen coordinates
        screen_x = best_wisp['center'][0] + 300
        screen_y = best_wisp['center'][1] + 300

        print(f"Wisp found at screen coordinates: ({screen_x}, {screen_y})")
        print(f"Area: {best_wisp['area']}, Circularity: {best_wisp['circularity']:.2f}, Hue: {best_wisp['hue']:.1f}")

        return ('wisp', screen_x, screen_y)

    print("No wisps detected")
    return None


def findEnergyRift():
    """Find energy rift using precise color and shape detection"""

    # Take screenshot
    screenshot = pyautogui.screenshot(region=(300, 300, 400, 400))
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # Save for debugging
    cv2.imwrite('rift_original.png', screenshot_bgr)

    # Convert to HSV
    hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)

    # Energy rifts are BRIGHT LIME-GREEN/YELLOW-GREEN (much brighter than background)
    # Tighter hue range, HIGH saturation and value to avoid dark green terrain
    lower_rift = np.array([40, 120, 150])  # Yellow-green, high saturation, bright
    upper_rift = np.array([70, 255, 255])

    mask = cv2.inRange(hsv, lower_rift, upper_rift)

    # Apply morphological closing to connect rift segments split by terrain
    kernel = np.ones((15, 15), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Clean up noise
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

    # Save mask for debugging
    cv2.imwrite('rift_mask.png', mask)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Collect candidates with detailed analysis
    rift_candidates = []
    rejected_candidates = []

    for contour in contours:
        area = cv2.contourArea(contour)

        # Get bounding box
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate center
        center_x = x + w // 2
        center_y = y + h // 2

        # Calculate circularity
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

        # Calculate mean HSV for this object
        mask_single = np.zeros(screenshot_bgr.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask_single, [contour], -1, 255, -1)
        mean_hsv = cv2.mean(hsv, mask=mask_single)
        mean_hue = mean_hsv[0]
        mean_saturation = mean_hsv[1]
        mean_value = mean_hsv[2]

        # Energy rift characteristics:
        # - LARGE area (>3000 pixels even when partially occluded)
        # - VERY BRIGHT (high value)
        # - IRREGULAR shape (low circularity < 0.5)
        # - HIGH saturation
        if area > 3000 and mean_value > 150 and mean_saturation > 100:
            rift_candidates.append({
                'center': (center_x, center_y),
                'area': area,
                'circularity': circularity,
                'contour': contour,
                'hue': mean_hue,
                'saturation': mean_saturation,
                'value': mean_value
            })
        else:
            rejected_candidates.append({
                'center': (center_x, center_y),
                'area': area,
                'value': mean_value,
                'reason': f"A:{int(area)} V:{int(mean_value)}"
            })

    # Debug visualization
    debug_image = screenshot_bgr.copy()

    # Draw rejected candidates in blue
    for obj in rejected_candidates:
        cv2.circle(debug_image, obj['center'], 5, (255, 0, 0), 2)
        cv2.putText(debug_image, obj['reason'], (obj['center'][0], obj['center'][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

    # Draw rift candidates in red
    for candidate in rift_candidates:
        cv2.drawContours(debug_image, [candidate['contour']], -1, (0, 0, 255), 3)
        label = f"RIFT A:{int(candidate['area'])} H:{int(candidate['hue'])} V:{int(candidate['value'])}"
        cv2.putText(debug_image, label, (candidate['center'][0] - 50, candidate['center'][1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    cv2.imwrite('rift_detected.png', debug_image)

    # Sort by area (largest first) - rift will be the largest bright yellow-green object
    if rift_candidates:
        rift_candidates.sort(key=lambda x: x['area'], reverse=True)
        best_rift = rift_candidates[0]

        # Convert to screen coordinates
        screen_x = best_rift['center'][0] + 300
        screen_y = best_rift['center'][1] + 300

        print(f"Energy rift found at: ({screen_x}, {screen_y})")
        print(f"  Area: {best_rift['area']}, Hue: {best_rift['hue']:.1f}, Value: {best_rift['value']:.1f}, Sat: {best_rift['saturation']:.1f}")

        return ('rift', screen_x, screen_y)

    print("Energy rift not found")
    print(f"  Rejected {len(rejected_candidates)} candidates (too small or too dark)")
    return None


def rotateCamera():
    """Rotate camera using arrow keys to find wisps"""
    direction = random.choice(['left', 'right'])
    duration = random.uniform(0.5, 1.5)  # Random rotation duration

    print(f"Rotating camera {direction} for {duration:.1f} seconds...")

    # Press and hold arrow key
    pyautogui.keyDown(direction)
    time.sleep(duration)
    pyautogui.keyUp(direction)

    # Small delay after rotation
    time.sleep(0.5)


def divinationBot():
    """Simplified Divination bot with better timing"""

    print("Starting Divination bot...")
    print("Press Ctrl+C to stop")

    wisp_harvest_count = 0
    max_harvests_before_rift = 1  # Harvest once before going to rift

    try:
        while True:
            # Look for wisps
            result = findWispWithBlobDetection()

            if result and result[0] == 'wisp':
                _, x, y = result

                # Random click duration
                click_duration = random.uniform(0.4, 0.6)
                print(f"Clicking wisp at ({x}, {y}) with {click_duration:.2f}s movement")

                pyautogui.moveTo(x, y, duration=click_duration)
                pyautogui.click()

                # Random harvest time between 30-40 seconds
                harvest_time = random.uniform(30, 40)
                print(f"Harvesting for {harvest_time:.1f} seconds...")

                time.sleep(harvest_time)

                wisp_harvest_count += 1
                print(f"Completed harvest #{wisp_harvest_count}")

                # Check if it's time to convert at rift
                if wisp_harvest_count >= max_harvests_before_rift:
                    print(f"Time to convert at rift (after {wisp_harvest_count} harvests)")

                    # Try to find and click the rift with retries
                    max_rift_attempts = 8
                    rift_found = False

                    for attempt in range(max_rift_attempts):
                        print(f"Looking for energy rift (attempt {attempt + 1}/{max_rift_attempts})...")
                        rift_result = findEnergyRift()

                        if rift_result:
                            _, rift_x, rift_y = rift_result

                            # Random click duration
                            click_duration = random.uniform(0.4, 0.6)
                            print(f"Clicking energy rift at ({rift_x}, {rift_y})")

                            pyautogui.moveTo(rift_x, rift_y, duration=click_duration)
                            pyautogui.click()

                            # Random conversion time between 30-40 seconds
                            convert_time = random.uniform(30, 40)
                            print(f"Converting memories for {convert_time:.1f} seconds...")

                            time.sleep(convert_time)

                            # Reset counter for next cycle
                            wisp_harvest_count = 0
                            max_harvests_before_rift = 1
                            print(f"Next rift visit after {max_harvests_before_rift} harvest")

                            rift_found = True
                            break
                        else:
                            print("Energy rift not found, rotating camera...")
                            rotateCamera()
                            time.sleep(1)  # Wait a bit after rotation

                    if not rift_found:
                        print(f"WARNING: Could not find energy rift after {max_rift_attempts} attempts!")
                        print("Continuing with wisp harvesting...")
            else:
                print("No wisps found, rotating camera...")
                rotateCamera()

                # Small delay before trying again
                time.sleep(1)

    except KeyboardInterrupt:
        print(f"\nBot stopped. Total harvests completed: {wisp_harvest_count}")


# Run the bot
if __name__ == "__main__":
    # Run the full divination bot
    divinationBot()

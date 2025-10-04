import pyautogui
import cv2
import numpy as np
import time

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
    
    # Define HSV ranges for wisp colors
    # Bright greens/yellows (typical wisp colors)
    lower_bright = np.array([40, 100, 100])  # Hue, Saturation, Value
    upper_bright = np.array([80, 255, 255])
    
    # Blue-greens (alternative wisp colors)
    lower_blue_green = np.array([80, 50, 50])
    upper_blue_green = np.array([110, 255, 255])
    
    # Create masks for both color ranges
    mask_bright = cv2.inRange(hsv, lower_bright, upper_bright)
    mask_blue_green = cv2.inRange(hsv, lower_blue_green, upper_blue_green)
    
    # Combine masks
    mask = cv2.bitwise_or(mask_bright, mask_blue_green)
    
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
    rift_candidate = None
    
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
        
        # Energy rifts are typically larger and more elongated/irregular
        if area > 5000 or (area > 2000 and circularity < 0.3):
            # This is likely the energy rift
            rift_candidate = {
                'center': (center_x, center_y),
                'area': area,
                'circularity': circularity,
                'contour': contour
            }
        # Wisps are smaller and more circular
        elif 50 < area < 2000:  # Reduced upper limit to exclude rifts
            # Wisps are usually somewhat circular/oval
            if 0.5 < aspect_ratio < 2.0 and circularity > 0.4:  # Increased circularity threshold
                wisp_candidates.append({
                    'center': (center_x, center_y),
                    'area': area,
                    'circularity': circularity,
                    'contour': contour
                })
    
    # Debug visualization
    debug_image = screenshot_bgr.copy()
    
    # Draw rift in red
    if rift_candidate:
        cv2.drawContours(debug_image, [rift_candidate['contour']], -1, (0, 0, 255), 2)
        cv2.putText(debug_image, "RIFT", rift_candidate['center'], 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Draw wisps in green
    for candidate in wisp_candidates:
        cv2.drawContours(debug_image, [candidate['contour']], -1, (0, 255, 0), 2)
        cv2.circle(debug_image, candidate['center'], 3, (255, 0, 0), -1)
    
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
        print(f"Area: {best_wisp['area']}, Circularity: {best_wisp['circularity']:.2f}")
        
        return ('wisp', screen_x, screen_y)
    
    print("No wisps detected")
    return None


def findEnergyRift():
    """Specifically find the energy rift"""
    
    # Take screenshot
    screenshot = pyautogui.screenshot(region=(300, 300, 400, 400))  # Adjust region as needed
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Convert to HSV
    hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)
    
    # Energy rifts are bright green
    lower_bright = np.array([40, 100, 100])
    upper_bright = np.array([80, 255, 255])
    
    mask = cv2.inRange(hsv, lower_bright, upper_bright)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for large, irregular shapes (rifts)
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area > 3000:  # Rifts are large
            # Get center
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Convert to screen coordinates
                screen_x = cx + 300
                screen_y = cy + 300
                
                print(f"Energy rift found at: ({screen_x}, {screen_y})")
                return ('rift', screen_x, screen_y)
    
    print("Energy rift not found")
    return None


def findWispSimplified():
    """Simplified version using template matching if you have a good wisp image"""
    
    # Take screenshot
    screenshot = pyautogui.screenshot(region=(300, 300, 400, 400))
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Convert to HSV
    hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)
    
    # Create a mask for bright colors (wisps are usually bright)
    # This focuses on high value (brightness) and high saturation
    lower = np.array([0, 50, 150])   # Any hue, medium saturation, high brightness
    upper = np.array([180, 255, 255])
    
    mask = cv2.inRange(hsv, lower, upper)
    
    # Find bright blobs
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest bright blob
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get center
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            
            # Convert to screen coordinates
            screen_x = cx + 300
            screen_y = cy + 300
            
            print(f"Wisp found at: ({screen_x}, {screen_y})")
            return (screen_x, screen_y)
    
    return None


def clickWisp():
    """Click on detected wisp"""
    # Try blob detection first
    wisp_location = findWispWithBlobDetection()
    
    # If blob detection fails, try simplified method
    if not wisp_location:
        print("Blob detection failed, trying simplified method...")
        wisp_location = findWispSimplified()
    
    if wisp_location:
        pyautogui.moveTo(wisp_location[0], wisp_location[1], duration=0.5)
        pyautogui.click()
        print("Clicked on the wisp at:", wisp_location)
        return True
    else:
        print("Wisp not found, cannot click.")
        return False


def continuousWispHunting(interval=3):
    """Continuously hunt wisps"""
    print("Starting wisp hunting... Press Ctrl+C to stop")
    
    try:
        while True:
            if clickWisp():
                print("Waiting for wisp to be harvested...")
                time.sleep(3)  # Wait for harvest animation
            else:
                print(f"No wisp found, checking again in {interval} seconds...")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nStopped wisp hunting")


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
    
    # Define HSV ranges for wisp colors
    # Bright greens/yellows (typical wisp colors)
    lower_bright = np.array([40, 100, 100])  # Hue, Saturation, Value
    upper_bright = np.array([80, 255, 255])
    
    # Blue-greens (alternative wisp colors)
    lower_blue_green = np.array([80, 50, 50])
    upper_blue_green = np.array([110, 255, 255])
    
    # Create masks for both color ranges
    mask_bright = cv2.inRange(hsv, lower_bright, upper_bright)
    mask_blue_green = cv2.inRange(hsv, lower_blue_green, upper_blue_green)
    
    # Combine masks
    mask = cv2.bitwise_or(mask_bright, mask_blue_green)
    
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
    rift_candidate = None
    
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
        
        # Energy rifts are typically larger and more elongated/irregular
        if area > 5000 or (area > 2000 and circularity < 0.3):
            # This is likely the energy rift
            rift_candidate = {
                'center': (center_x, center_y),
                'area': area,
                'circularity': circularity,
                'contour': contour
            }
        # Wisps are smaller and more circular
        elif 50 < area < 2000:  # Reduced upper limit to exclude rifts
            # Wisps are usually somewhat circular/oval
            if 0.5 < aspect_ratio < 2.0 and circularity > 0.4:  # Increased circularity threshold
                wisp_candidates.append({
                    'center': (center_x, center_y),
                    'area': area,
                    'circularity': circularity,
                    'contour': contour
                })
    
    # Debug visualization
    debug_image = screenshot_bgr.copy()
    
    # Draw rift in red
    if rift_candidate:
        cv2.drawContours(debug_image, [rift_candidate['contour']], -1, (0, 0, 255), 2)
        cv2.putText(debug_image, "RIFT", rift_candidate['center'], 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Draw wisps in green
    for candidate in wisp_candidates:
        cv2.drawContours(debug_image, [candidate['contour']], -1, (0, 255, 0), 2)
        cv2.circle(debug_image, candidate['center'], 3, (255, 0, 0), -1)
    
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
        print(f"Area: {best_wisp['area']}, Circularity: {best_wisp['circularity']:.2f}")
        
        return ('wisp', screen_x, screen_y)
    
    print("No wisps detected")
    return None


def findEnergyRift():
    """Specifically find the energy rift"""
    
    # Take screenshot
    screenshot = pyautogui.screenshot(region=(300, 300, 400, 400))  # Adjust region as needed
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    
    # Convert to HSV
    hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)
    
    # Energy rifts are bright green
    lower_bright = np.array([40, 100, 100])
    upper_bright = np.array([80, 255, 255])
    
    mask = cv2.inRange(hsv, lower_bright, upper_bright)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Look for large, irregular shapes (rifts)
    for contour in contours:
        area = cv2.contourArea(contour)
        
        if area > 3000:  # Rifts are large
            # Get center
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Convert to screen coordinates
                screen_x = cx + 300
                screen_y = cy + 300
                
                print(f"Energy rift found at: ({screen_x}, {screen_y})")
                return ('rift', screen_x, screen_y)
    
    print("Energy rift not found")
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
    max_harvests_before_rift = random.randint(8, 12)  # Random number of harvests before going to rift
    
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
                    
                    # Find and click the rift
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
                        
                        # Reset counter and randomize next rift visit
                        wisp_harvest_count = 0
                        max_harvests_before_rift = random.randint(8, 12)
                        print(f"Next rift visit after {max_harvests_before_rift} harvests")
                    else:
                        print("Could not find energy rift! Rotating camera...")
                        rotateCamera()
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
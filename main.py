import random
import pyautogui
import os



def findWisp():
    # We should take a screenshot of the region where we expect to find the wisp
    screenshot = pyautogui.screenshot(region=(300, 300, 400, 400))  # Adjust region as needed
    screenshot.save('screenshot.png')
    
    # Updated wisp colors based on your data analysis
    # Bright greens and blue-greens that likely represent wisps
    wisp_colours = [
        # Original colors
        (71, 138, 130), (95, 176, 176), (171, 210, 225),
        (46, 84, 49), (63, 111, 83), (55, 88, 67),
        (77, 150, 145), (81, 155, 152), (83, 159, 156),
        (86, 161, 161), (97, 146, 167), (116, 147, 158),
        (148, 186, 205), (143, 175, 184),
        # Additional blue-green variations
        (72, 111, 108), (67, 131, 120), (86, 124, 126),
        (58, 113, 112), (56, 109, 94), (55, 102, 80),
        (52, 85, 58), (43, 77, 41), (40, 82, 34)
    ]
    
    def is_terrain_color(color):
        """Filter out dark/medium green terrain colors"""
        r, g, b = color
        # Terrain colors typically have:
        # - Red: 20-65
        # - Green: 40-90
        # - Blue: 0-30
        # - And green is dominant but not too bright
        if (20 <= r <= 65 and 40 <= g <= 90 and 0 <= b <= 30 and 
            g > r and g < 100):  # Green dominant but not bright
            return True
        
        # Also filter very dark colors (shadows/borders)
        if r <= 30 and g <= 40 and b <= 10:
            return True
            
        return False
    
    # Now we should sample up to 500 random pixels in the screenshot to see if any match the wisp colors
    for _ in range(1000):
        x = random.randint(0, screenshot.width - 1)
        y = random.randint(0, screenshot.height - 1)
        pixel_color = screenshot.getpixel((x, y))
        
        # Skip terrain colors
        if is_terrain_color(pixel_color):
            continue
            
        print(f"Checking pixel at ({x}, {y}) with color {pixel_color}")
        if pixel_color in wisp_colours:
            # Convert back to screen coordinates
            screen_x = x + 300
            screen_y = y + 300
            print(f"Wisp color found at screen coordinates: ({screen_x}, {screen_y}) with color {pixel_color}")
            return (screen_x, screen_y) # Return screen coordinates
    print("Wisp not found in sampled pixels.")
    return None

def findEnergyRift():
    # Placeholder function for finding energy rift
    # Implement similar logic as findWisp with appropriate colors and region
    pass

def clickEnergyRift():
        energy_rift_colours = [
        (191, 234, 119), (191, 235, 119), (191, 235, 120),
        (193, 233, 111), (193, 234, 112), (193, 234, 113),
        (195, 234, 125), (195, 232, 106), (195, 226, 111),
        (196, 232, 109), (198, 229, 95), (198, 230, 97),
        (200, 236, 137), (189, 233, 79), (189, 234, 88),
        (189, 231, 115), (187, 221, 111), (185, 235, 111),
        (174, 236, 97), (177, 236, 102), (179, 236, 62),
        (151, 237, 69), (145, 237, 62), (142, 237, 58),
        (163, 236, 85), (169, 62, 0), 
    ]

def clickWisp():
    wisp_location = findWisp()
    if wisp_location:
        pyautogui.moveTo(wisp_location[0], wisp_location[1], duration=0.5)
        pyautogui.click()
        print("Clicked on the wisp at:", wisp_location)
    else:
        print("Wisp not found, cannot click.")

clickWisp()

# Move mouse to (100, 200) and click
# pyautogui.moveTo(100, 200, duration=0.5)
# pyautogui.click()
# # Toggle Caps Lock and type
# pyautogui.press('capslock')  # Toggle on/off
# pyautogui.write('Hello, World!', interval=0.1)

# # Capture screen region and save
# screenshot = pyautogui.screenshot(region=(0, 0, 300, 400))
# screenshot.save('capture.png')




# def main():
#     print("Automation script executed.")
#     sleep(2)  # Pause for 2 seconds
    
#     while True:
#         findWisp()
    
     
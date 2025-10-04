def findWispCV():
    # Check if image exists
    if not os.path.exists('wisp_wiki.png'):
        print("Error: wisp.png not found in current directory")
        return None
    
    try:
        wisp_location = pyautogui.locateOnScreen('wisp2-clean.png', confidence=0.3)
        if wisp_location:
            print("Wisp found at:", wisp_location)
            return wisp_location
        else:
            print("Wisp not found.")
            return None
    except pyautogui.ImageNotFoundException:
        print("Could not locate the wisp on screen")
        return None
def clickWispCV():
    wisp_location = findWispCV()
    if wisp_location:
        wisp_center = pyautogui.center(wisp_location)
        pyautogui.moveTo(wisp_center.x, wisp_center.y, duration=0.5)
        pyautogui.click()
        print("Clicked on the wisp at:", wisp_center)
    else:
        print("Wisp not found, cannot click.")

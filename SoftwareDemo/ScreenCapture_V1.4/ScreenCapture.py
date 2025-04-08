# Imports
import pygetwindow as gw
import pyautogui
import time

# Print all window titles
for window in gw.getAllTitles():
    print(window)

# Keyword to search for in the title
keyword = "192.168.1.106" # Replace inside of quote with camera IP address

# Find window that contains the keyword in title
target_window = None
for title in gw.getAllTitles():
    if keyword.lower() in title.lower():
        target_window = title
        break

if target_window:
    print(f"Found window: {target_window}")
    try:
        win = gw.getWindowsWithTitle(target_window)[0]  # Get the first matching window
        if win:
            # Bring the window to the front
            win.activate()

            # Delay added incase it's taking screenshot too fast. Sometimes it captures window, sometimes it captures VSC 
            time.sleep(.5) # Half-second delay

            # Capture screenshot of the window
            screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))

            #FIXME Send window back
            # bruh 

            # File path for saved screenshot
            screenshot.save(r"C:\GitHub\SafeHaven\Samples\HTTP_Test.png")     # REPLACE USER_HERE WITH COMPUTER USERNAME
            # Screenshot save directory can be changed accordingly

            print("Screenshot saved as 'Screenshot.png'")
        
    except Exception as e:
        print("Window not found!", e)
else:
    print(f"Window not found with {keyword}!")
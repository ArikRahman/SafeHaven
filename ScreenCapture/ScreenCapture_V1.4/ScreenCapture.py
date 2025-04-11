# Imports
import pygetwindow as gw
import pyautogui
import time

# Print all window titles
for window in gw.getAllTitles():
    print(window)

# Keyword to search for in the title
# keyword = "192.168.1.106" # Replace inside of quote with camera IP address
keyword1 = "Employee_Theft" # Replace inside of quote with camera IP address
keyword2 = "Visual Studio Code" # Replace place of quote with VSC or cmd

# Initialize variables to store window titles
target_window_title = None
home_window_title = None

# Find window that contains the keyword in title
for title in gw.getAllTitles():
    if keyword1.lower() in title.lower():
        target_window_title = title
    if keyword2.lower() in title.lower():
        home_window_title = title

# Print test statement to see if windows are found
if target_window_title and home_window_title:
    print(f"Found window: {target_window_title}")
    print(f"Found window: {home_window_title}")
    
    try:
        # Get the first matching window
        target_win = gw.getWindowsWithTitle(target_window_title)[0]
        home_win = gw.getWindowsWithTitle(home_window_title)[0]
        
        # Bring the browser window to the front
        target_win.activate()

        # Delay added incase it's taking screenshot too fast. Sometimes it captures window, sometimes it captures VSC 
        time.sleep(0.5) # Half-second delay

        # Capture screenshot of the window
        screenshot = pyautogui.screenshot(region=(target_win.left, target_win.top, target_win.width, target_win.height))

        # Restore home window (your VSC/cmd) if minimized
        home_win.minimize()
        time.sleep(0.5)
        home_win.restore()
        time.sleep(0.5)

        # File path for saved screenshot
        screenshot.save(r"C:\GitHub\SafeHaven\Samples\TemporaryTest.png")     # REPLACE USER_HERE WITH COMPUTER USERNAME
        
        # Screenshot save directory can be changed accordingly
        print("Screenshot saved as 'Screenshot.png'")
        
    except Exception as e:
        print("Window not found!", e)
else:
    print(f"Window not found with {keyword1}!")
    print(f"Window not found with {keyword2}!")
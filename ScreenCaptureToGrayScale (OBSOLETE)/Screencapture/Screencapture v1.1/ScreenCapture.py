# Install these in the terminal to download packages
# pip install pyautogui --use-pep517
# pip install numpy
# pip install opencv-python
# pip install pyautogui pygetwindow opencv-python
# pip install --upgrade pyautogui pyscreeze pillow
# pip install pillow==9.5.0
# pip install pygetwindow pyautogui pyscreeze
# pip install --upgrade Pillow

"""import pygetwindow as gw
import pyautogui

# Print all window titles
for window in gw.getAllTitles():
    print(window)"""
# UNCOMMENT TOP BLOCK AND COMMENT BOTTOM TO GET WINDOW NAME
# COMMENT OUT TOP BLOCK AND UNCOMMENT BOTTOM BLOCK

import pygetwindow as gw
import pyautogui

# Window title
window_title = ""  # PUT WINDOW NAME INSIDE ""

# Get window by title
try:
    win = gw.getWindowsWithTitle(window_title)[0]  # Get the first matching window
    if win:
        # Bring the window to the front
        win.activate()

        # Capture screenshot of the window
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))

        # Save the screenshot with a correct file path
        # Use forward slashes or raw string
        screenshot.save(r"C:/Users/USER_HERE/Downloads/window_capture.png")     # REPLACE USER_HERE WITH COMPUTER USERNAME
        # Screenshot save directory can be changed accordingly

        print("Screenshot saved as 'window_capture.png'")
    else:
        print("Window not found!")
except IndexError:
    print("Window not found! Check if the title is correct.")

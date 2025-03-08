# Copy and paste these in the terminal to download packages
# pip install pyautogui --use-pep517
# pip install numpy
# pip install opencv-python
# pip install pyautogui pygetwindow opencv-python
# pip install --upgrade pyautogui pyscreeze pillow
# pip install pillow==9.5.0
# pip install pygetwindow pyautogui pyscreeze
# pip install --upgrade Pillow

import pygetwindow as gw
import pyautogui
import time

# Print all window titles
for window in gw.getAllTitles():
    print(window)

# Window title
window_title = ""  # PUT WINDOW NAME INSIDE ""

# Get window by title
try:
    win = gw.getWindowsWithTitle(window_title)[0]  # Get the first matching window
    if win:
        # Bring the window to the front
        win.activate()

        # Delay added incase it's taking screenshot too fast. Other instances it captures window,
        # other instanaces it captures VSC

        # Half-second delay
        time.sleep(.5) 

        # Capture screenshot of the window
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))

        # Save the screenshot with a correct file path
        # Use forward slashes or raw string
        screenshot.save(r"C:\Users\vguo9\OneDrive\Desktop\Year 4 and F25\Y4S2\ESET419-932\Software\Samples\Screenshot.png")     # REPLACE USER_HERE WITH COMPUTER USERNAME
        # Screenshot save directory can be changed accordingly

        print("Screenshot saved as 'Screenshot.png'")
    else:
        print("Window not found!")
except IndexError:
    print("Window not found! Check if the title is correct.")
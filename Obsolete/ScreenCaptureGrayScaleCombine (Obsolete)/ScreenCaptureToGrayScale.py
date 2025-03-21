# Copy these in the terminal to download packages
# pip install pyautogui --use-pep517
# pip install numpy
# pip install opencv-python
# pip install pyautogui pygetwindow opencv-python
# pip install --upgrade pyautogui pyscreeze pillow
# pip install pillow==9.5.0
# pip install pygetwindow pyautogui pyscreeze
# pip install --upgrade Pillow
# pip3 install torch torchvision torchaudio

import pygetwindow as gw
import pyautogui
import time

from PIL import Image

# Print all window titles
for window in gw.getAllTitles():
    print(window)

# Start of screen capture program
# Window title
window_title = "person_standing.png (640×480) - Google Chrome"  # PUT WINDOW NAME INSIDE ""

# Get window by title
try:
    win = gw.getWindowsWithTitle(window_title)[0]  # Get the first matching window
    if win:
        # Bring the window to the front
        win.activate()

        # Delay added in case it's taking screenshot too fast. Other instances it captures window,
        # other instanaces it captures VSC

        # Half-second delay
        time.sleep(.5) 

        # Capture screenshot of the window
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))

        # Save the screenshot with a correct file path
        # Use forward slashes or raw string
        screenshot.save(r"C:\419Software\Samples\Screenshot.png")     # REPLACE PATH WITH DIRECTORY PATH TO STORE SCREENSHOTS

        print("Screenshot saved as 'Screenshot.png'")
    else:
        print("Window not found!")
except IndexError:
    print("Window not found! Check if the title is correct.")

# Start of grayscale conversion program
# Path to the original screenshot
original_image_path = r"C:\419Software\Samples\Screenshot.png" # REPLACE PATH WITH DIRECTORY TO SCREENSHOT

# Open the original image
original_image = Image.open(original_image_path)

# Convert the image to grayscale
grayscale_image = original_image.convert("L")

# Save the grayscale image (you can choose a new file name if you want)
grayscale_image_path = r"C:\419Software\Samples\Grayscale.png" # REPLACE PATH
grayscale_image.save(grayscale_image_path)

# Display the grayscale image (optional)
grayscale_image.show()

print("Grayscale image saved as 'Grayscale.png'")
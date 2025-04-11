# Object detection in this project is powered by YOLOv5 by Ultralytics
# GitHub: https://github.com/ultralytics/yolov5
# DOI: https://doi.org/10.5281/zenodo.3908559
# Licensed under AGPL-3.0

# Screen Capture Imports
import pygetwindow as gw
import pyautogui
import time

# Boundary Detect Imports
import torch
import cv2

# Snake Path Algorithm Imports
import numpy as np

# Pyplot Import
import matplotlib.pyplot as plt

# Load the YOLOv5 model (small version for speed)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# ███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗     ██████╗ █████╗ ██████╗ ████████╗██╗   ██╗██████╗ ███████╗
# ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║    ██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██╔════╝
# ███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║    ██║     ███████║██████╔╝   ██║   ██║   ██║██████╔╝█████╗  
# ╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║    ██║     ██╔══██║██╔═══╝    ██║   ██║   ██║██╔══██╗██╔══╝  
# ███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║    ╚██████╗██║  ██║██║        ██║   ╚██████╔╝██║  ██║███████╗
# ╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝     ╚═════╝╚═╝  ╚═╝╚═╝        ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
# Print all window titles
# for window in gw.getAllTitles():
#     print(window)

# Keyword to search for in the title
# keyword = "192.168.x.x" # Replace inside of quote with camera IP address
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
        screenshot.save(r"C:\GitHub\SafeHaven\SoftwareDemo\Sample\Screenshot.png")     # REPLACE USER_HERE WITH COMPUTER USERNAME
        # Screenshot save directory can be changed accordingly
        
        print("Screenshot saved as 'Screenshot.png'")
        
    except Exception as e:
        print("Window not found!", e)
else:
    print(f"Window not found with {keyword1}!")
    print(f"Window not found with {keyword2}!")   

# ██████╗  ██████╗ ██╗   ██╗███╗   ██╗██████╗  █████╗ ██████╗ ██╗   ██╗    ██████╗ ███████╗████████╗███████╗ ██████╗████████╗    ██╗   ██╗  ██╗██████╗ 
# ██╔══██╗██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝    ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝    ██║   ██║ ███║╚════██╗
# ██████╔╝██║   ██║██║   ██║██╔██╗ ██║██║  ██║███████║██████╔╝ ╚████╔╝     ██║  ██║█████╗     ██║   █████╗  ██║        ██║       ██║   ██║ ╚██║ █████╔╝
# ██╔══██╗██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██║██╔══██╗  ╚██╔╝      ██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║       ╚██╗ ██╔╝  ██║██╔═══╝ 
# ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║██║  ██║   ██║       ██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║        ╚████╔╝██╗██║███████╗
# ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝         ╚═══╝ ╚═╝╚═╝╚══════╝
                                                                                                                                                     
# Load the image
image_path = r"C:\GitHub\SafeHaven\SoftwareDemo\Sample\Screenshot.png"  # Change to your image path
image = cv2.imread(image_path)

# Convert BGR to RGB (YOLO expects RGB format)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Run YOLOv5 on the image
results = model(image_rgb)

# Print cord format
print("Pixel Cord Format: (x1, y1), (x2, y2) \n")

# Extract bounding box coordinates
for *box, conf, cls in results.xyxy[0]:  # Loop through detected objects
    x1, y1, x2, y2 = map(int, box)  # Convert to integers
    label = model.names[int(cls)]  # Get class label (e.g., "person")

    if label == "person":  # Filter only people
        print(f"Bounding Box Coordinates in Pixel: ({x1}, {y1}), ({x2}, {y2})")
        
        # Declare variable to store pixel to meter conversion values
        # X - Pixel to meter conversion ratio
        X_Px_to_M = 0.00092592592
        xm1, xm2 = x1 * X_Px_to_M, x2 * X_Px_to_M

        # Y - Pixel to meter conversion ratio
        Y_Px_to_M = 0.00052083333
        ym1, ym2 = y1 * Y_Px_to_M, y2* Y_Px_to_M
        
        # FIXME: from online pixel to meter conversion ratio is 0.000265
        # find out what our relative pixel conversion should be
        
        # Convert pixel to meter
        print(f"Bound Box Coordinates in Meter: ({xm1:.4f}, {ym1:.4f}), ({xm2:.4f}, {ym2:.4f}) \n")
        
        # Draw the bounding box on the image
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red box
        cv2.putText(image, f"{label}. Conf: {100*conf:.1f}%", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Export variables
import json

data = {
    "xm1": xm1,
    "ym1": ym1,
    "xm2": xm2,
    "ym2": ym2
}

# Save to a specific file
file_path = r"C:\GitHub\SafeHaven\SoftwareDemo\coords.json"  # or use full path like "C:/Users/yourname/Desktop/coords.json"

# Make sure the directory exists before saving
import os
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Write JSON
with open(file_path, "w") as f:
    json.dump(data, f, indent=4)  # indent=4 makes it readable

# Save or display the image
cv2.imshow("YOLOv5 Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
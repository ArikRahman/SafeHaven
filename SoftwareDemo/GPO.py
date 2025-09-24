# Object detection in this project is powered by YOLOv11 by Ultralytics
# GitHub: https://github.com/ultralytics/yolov11
# DOI: https://doi.org/10.5281/zenodo.3908559
# Licensed under AGPL-3.0

# Command line: python3 .\GPO.py; python3 .\SnakePathAlgorithm.py

# On both dev machine and Pi: install with the command line at the bottom
# python -m pip install -U ultralytics

# On the Pi install the following:
# sudo apt update
# sudo apt install -y python3-pip libcamera-dev python3-libcamera python3-kms++ python3-picamera2
# python -m pip install -U ultralytics opencv-python

# Screen Capture Imports
import pygetwindow as gw
import pyautogui
import time

# Boundary Detect Imports
import torch
import cv2
from ultralytics import YOLO
import os

# Snake Path Algorithm Imports
import json
import numpy as np

# Pyplot Import
import matplotlib.pyplot as plt

# YOLOv11 set up
YOLO_WEIGHTS = r"yolo11s.pt"
YOLO_IMGSZ = 640
YOLO_CONF = 0.40

ALLOWED_CLASSES = {"person", "mannequin"}

model = YOLO(YOLO_WEIGHTS)

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

#  ██████╗ ██████╗      ██╗███████╗ ██████╗████████╗    ██████╗ ███████╗████████╗███████╗ ██████╗████████╗██╗ ██████╗ ███╗   ██╗
# ██╔═══██╗██╔══██╗     ██║██╔════╝██╔════╝╚══██╔══╝    ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██║   ██║██████╔╝     ██║█████╗  ██║        ██║       ██║  ██║█████╗     ██║   █████╗  ██║        ██║   ██║██║   ██║██╔██╗ ██║
# ██║   ██║██╔══██╗██   ██║██╔══╝  ██║        ██║       ██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║   ██║██║   ██║██║╚██╗██║
# ╚██████╔╝██████╔╝╚█████╔╝███████╗╚██████╗   ██║       ██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║   ██║╚██████╔╝██║ ╚████║
#  ╚═════╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝       ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                                                                                    
# Load the image
image_path = r"C:\GitHub\SafeHaven\SoftwareDemo\Sample\Screenshot.png"  # Change to your image path
image = cv2.imread(image_path)
if image is None:
    raise FileNotFoundError(f"Could not read image at {image_path}")

# Run YOLOv11 on the image
results = model.predict(source=image, imgsz=YOLO_IMGSZ, conf=YOLO_CONF, device='cpu', verbose=False)

# Print cord format
print("Pixel Cord Format: (x1, y1), (x2, y2) \n")

# Pixel to meter conversion
X_Px_to_M = 0.00092592592
Y_Px_to_M = 0.00052083333

def class_name(m, cls_id: int) -> str:
    names = getattr(m, "names", None)
    if isinstance(names, dict):
        return names.get(cls_id, str(cls_id))
    if isinstance(names, list) and 0 <= cls_id < len(names):
        return names[cls_id]
    return str(cls_id)

best = None  # (area, (x1,y1,x2,y2), label, conf)

if len(results):
    r = results[0]
    for b in r.boxes:
        x1, y1, x2, y2 = b.xyxy[0].cpu().numpy().astype(int).tolist()
        cls_id = int(b.cls[0].item())
        conf   = float(b.conf[0].item())
        label  = class_name(model, cls_id)

        if label in ALLOWED_CLASSES:
            area = max(0, x2 - x1) * max(0, y2 - y1)
            if best is None or area > best[0]:
                best = (area, (x1, y1, x2, y2), label, conf)

coords_out_path = r"C:\GitHub\SafeHaven\SoftwareDemo\coords.json"
os.makedirs(os.path.dirname(coords_out_path), exist_ok=True)

if best is not None:
    _, (x1, y1, x2, y2), label, conf = best

    # Treat mannequin as person for downstream consumers
    display_label = "person"

    print(f"Bounding Box in Pixels: ({x1}, {y1}), ({x2}, {y2})  [{label}→{display_label}, conf={conf:.3f}]")

    xm1, xm2 = x1 * X_Px_to_M, x2 * X_Px_to_M
    ym1, ym2 = y1 * Y_Px_to_M, y2 * Y_Px_to_M
    print(f"Bounding Box in Meter: ({xm1:.4f}, {ym1:.4f}), ({xm2:.4f}, {ym2:.4f})\n")

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.putText(image, f"{display_label} {100*conf:.1f}%", (x1, max(0, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Export meters for path generator
    with open(coords_out_path, "w") as f:
        json.dump({"xm1": xm1, "ym1": ym1, "xm2": xm2, "ym2": ym2}, f, indent=4)
    print(f"Saved ROI meters to: {coords_out_path}")
else:
    print("No person/mannequin detected — exporting empty coords.")
    with open(coords_out_path, "w") as f:
        json.dump({"xm1": None, "ym1": None, "xm2": None, "ym2": None}, f, indent=4)

cv2.imshow("YOLO11 Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
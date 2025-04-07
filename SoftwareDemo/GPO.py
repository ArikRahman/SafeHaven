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
for window in gw.getAllTitles():
    print(window)

# Keyword to search for in the title
keyword = "Employee_Theft" # Replace inside of quote with camera IP address

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
            screenshot.save(r"C:\GitHub\SafeHaven\SoftwareDemo\Sample\Screenshot.png")     # REPLACE USER_HERE WITH COMPUTER USERNAME
            # Screenshot save directory can be changed accordingly

            print("Screenshot saved as 'Screenshot.png'")
        
    except Exception as e:
        print("Window not found!", e)
else:
    print(f"Window not found with {keyword}!")     

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

# # ██████╗  █████╗ ████████╗██╗  ██╗     ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# # ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# # ██████╔╝███████║   ██║   ███████║    ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║
# # ██╔═══╝ ██╔══██║   ██║   ██╔══██║    ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# # ██║     ██║  ██║   ██║   ██║  ██║    ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# # ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
# def generate_snake_path(x_min, y_min, x_max, y_max, step_x, step_y, origin_x, origin_y):
#     """
#     Generates a snake pattern scan path inside a boundary box
    
#     Parameters:
#         x_min, y_min - Bottom-left corner of the box
#         x_max, y_max - Top-right corner of the box
#         step_x - Horizontal step size
#         step_y - Vertical step size
#         origin_x, origin_y - Origin coordinates (where the scan starts and ends)
    
#     Returns:
#         List of (x, y) coordinates in snake path order
#     """
    
#     path = [] # Store the path

#     # 1. Path from origin to starting position
#     x = origin_x
#     y = origin_y

#     path.append((x, y)) # Start at origin

#     start_start_index = 0

#     # Move vertically from (x_min, y_max) to (x_min, y_min)
#     while y > y_max:
#         y -= step_y
#         path.append((x, round(float(y), 4)))
    
#     # Move horizontally from (x_min, y_max) to (x_min, y_min)
#     x = x_min
#     path.append((x, round(float(y_max), 4)))  # Ensure we start at the correct y position
#     start_end_index = len(path)
    
#     # 2. Snake path generation
#     snake_start_index = start_end_index

#     direction = -1      # Start moving down (-1), invert and switch to up (1)
#     while x <= x_max:   # Loop until x coordinate is at or greater than right x-coordinate
#         # Move down
#         if direction == -1:
#             # np.arange(start, stop, step)
#             y_values = np.arange(y_max, y_min - step_y, -step_y)
#         # Moving up
#         else:    
#             y_values = np.arange(y_min, y_max + step_y, step_y)
        
#         for y in y_values:
#             path.append((x, round(float(y),4)))
        
#         # Small step to the right
#         x += step_x
        
#         # Flip vertical direction 
#         direction *= -1
#     snake_end_index =  len(path)
    
#     # 3. Path from end of snake path to origin (0, 150) 
#     x_end, y_end = path[-1]

#     if direction == 1:                      # Last move was up
#         path.append((x_end, origin_y))      # Move up to origin_y
#         path.append((origin_x, origin_y))   # Move left to origin_x
#     else:  # Last move was down
#         path.append((origin_x, y_end))      # Move left first
#         path.append((origin_x, origin_y))   # Then move up

#     return_start_index = snake_end_index - 1
#     return_end_index = len(path)

#     return path, (start_start_index, start_end_index), (snake_start_index, snake_end_index), (return_start_index, return_end_index)

# # Test Case
# # x_min, y_min = 0.2584, 0.0988  # Bottom-left corner of boundary
# # x_max, y_max = 0.6384, 1.3  # Top-right corner of boundary

# # Define boundary box (Example: 1.5m x 1.5m frame)
# x_min, y_min = xm1, ym1   # Bottom-left corner of boundary
# x_max, y_max = xm2, ym2      # Top-right corner of boundary
# step_x = 8/100                  # 5 cm horizontal steps 

# # FIXME: figure out formula to get horizontal step just right 
# # find out what delta_X should be (What is the width of the scan reading)

# step_y = 3/100  # 2 cm vertical steps

# origin_x, origin_y = 0, 1.5  # Origin at (0, 150 cm)

# # FIXME: fix the slant. points are shifted up or down 1

# # Generate scan path
# path, start_range, snake_range, return_range = generate_snake_path(
#     x_min, y_min, x_max, y_max, step_x, step_y, origin_x, origin_y
# )

# # Variable Test Print
# # print(path[:10])  # Prints the first 10 points in the snake path
# print("Start range: ", start_range)
# print("Snake range: ", snake_range)
# print("Return range: ", return_range)

# # ██╗   ██╗ █████╗ ██████╗ ████████╗    ████████╗██████╗  █████╗ ███╗   ██╗███████╗███╗   ███╗██╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
# # ██║   ██║██╔══██╗██╔══██╗╚══██╔══╝    ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝████╗ ████║██║██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
# # ██║   ██║███████║██████╔╝   ██║          ██║   ██████╔╝███████║██╔██╗ ██║███████╗██╔████╔██║██║███████╗███████╗██║██║   ██║██╔██╗ ██║
# # ██║   ██║██╔══██║██╔══██╗   ██║          ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║╚██╔╝██║██║╚════██║╚════██║██║██║   ██║██║╚██╗██║
# # ╚██████╔╝██║  ██║██║  ██║   ██║          ██║   ██║  ██║██║  ██║██║ ╚████║███████║██║ ╚═╝ ██║██║███████║███████║██║╚██████╔╝██║ ╚████║
# #  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                                                                   

# # import serial
# # import time

# # # Define serial COM port
# # ser = serial.Serial('/dev/ttyUSB0', 115200, timeout = 1)
# # time.sleep(2) # Wait for connection to establish

# # # Send Path list
# # coordinates = path

# # for x, y in coordinates:
# #     message = f"{x},{y}\n"
# #     ser.write(message.encode())   # Send data
# #     time.sleep(0.1)               # Delay to prevent instability

# # ser.close()

# # ██████╗ ██╗      ██████╗ ████████╗    ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# # ██╔══██╗██║     ██╔═══██╗╚══██╔══╝    ██║   ██║██║██╔════╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# # ██████╔╝██║     ██║   ██║   ██║       ██║   ██║██║███████╗██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# # ██╔═══╝ ██║     ██║   ██║   ██║       ╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# # ██║     ███████╗╚██████╔╝   ██║        ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# # ╚═╝     ╚══════╝ ╚═════╝    ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                                                                     
# # Plot of snake path to visualize path
# def plot_segment(path, idx_range, color, label):
#     segment = path[idx_range[0]:idx_range[1]]
#     if len(segment) >= 2:  # Must have at least two points to plot a line
#         X, Y = zip(*segment)
#         plt.plot(X, Y, marker='.', linestyle='-', color=color, label=label)

# plt.figure(figsize=(6, 6))                  # Size of generated output

# plot_segment(path, start_range, 'green', 'Start Path')
# plot_segment(path, snake_range, 'blue', 'Snake Path')
# plot_segment(path, return_range, 'purple', 'Return Path')

# plt.plot(origin_x, origin_y, 'ro')          # Origin point on plot
# plt.annotate("Origin", 
#     (origin_x - .05, 1.5 + .04))            # Plot origin plot
# plt.xlim(-0.1, 1.5 + 0.1)                   # Define X-limits
# plt.ylim(-0.1, 1.5 + 0.1)                   # Define Y-limits
# plt.xlabel("X (meters)")                    # X-axis label
# plt.ylabel("Y (meters)")                    # Y-axis label
# plt.title("Snake Path Scan")                # Title
# plt.minorticks_on()                         # Turn on minor ticks
# plt.grid()
# plt.legend()
# plt.show()
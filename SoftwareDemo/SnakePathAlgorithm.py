# ██████╗  █████╗ ████████╗██╗  ██╗     ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██████╔╝███████║   ██║   ███████║    ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔═══╝ ██╔══██║   ██║   ██╔══██║    ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║     ██║  ██║   ██║   ██║  ██║    ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                                                      
import numpy as np
import json
import matplotlib.pyplot as plt
import os

def generate_snake_path(x_min, y_min, x_max, y_max, step_x, step_y, origin_x, origin_y):
    """
    Generates a snake pattern scan path inside a boundary box
    
    Parameters:
        x_min, y_min - Bottom-left corner of the box
        x_max, y_max - Top-right corner of the box
        step_x - Horizontal step size
        step_y - Vertical step size
        origin_x, origin_y - Origin coordinates (where the scan starts and ends)
    
    Returns:
        List of (x, y) coordinates in snake path order
    """
    
    path = [] # Store the path

    # 1. Path from origin to starting position
    x = origin_x
    y = origin_y

    path.append((x, y)) # Start at origin

    start_start_index = 0

    # Move vertically from (x_min, y_max) to (x_min, y_min)
    while y > y_max:
        y -= step_y
        path.append((x, round(float(y), 4)))
    
    # Move horizontally from (x_min, y_max) to (x_min, y_min)
    x = x_min
    path.append((x, round(float(y_max), 4)))  # Ensure we start at the correct y position
    start_end_index = len(path)
    
    # 2. Snake path generation
    snake_start_index = start_end_index

    direction = -1      # Start moving down (-1), invert and switch to up (1)
    while x <= x_max:   # Loop until x coordinate is at or greater than right x-coordinate
        # Move down
        if direction == -1:
            # np.arange(start, stop, step)
            y_values = np.arange(y_max, y_min - step_y, -step_y)
        # Moving up
        else:    
            y_values = np.arange(y_min, y_max + step_y, step_y)
        
        for y in y_values:
            path.append((x, round(float(y),4)))
        
        # Small step to the right
        x += step_x
        
        # Flip vertical direction 
        direction *= -1
    snake_end_index =  len(path)
    
    # 3. Path from end of snake path to origin (0, 150) 
    x_end, y_end = path[-1]

    if direction == 1:                      # Last move was up
        path.append((x_end, origin_y))      # Move up to origin_y
        path.append((origin_x, origin_y))   # Move left to origin_x
    else:  # Last move was down
        path.append((origin_x, y_end))      # Move left first
        path.append((origin_x, origin_y))   # Then move up

    return_start_index = snake_end_index - 1
    return_end_index = len(path)

    return path, (start_start_index, start_end_index), (snake_start_index, snake_end_index), (return_start_index, return_end_index)

# Test Case
# x_min, y_min = 0.2584, 0.0988  # Bottom-left corner of boundary
# x_max, y_max = 0.6384, 1.3  # Top-right corner of boundary

# Import cords
file_path = r"C:\GitHub\SafeHaven\SoftwareDemo\Picamera\box_coords.json"

if not os.path.exists(file_path):
    raise FileNotFoundError(f"Latest detection file not found: {file_path}")

with open(file_path, "r") as f:
    meta = json.load(f)

det = meta.get("detection")
if det is None:
    raise ValueError("No detection in latest_box_coords.json (detection=None). Capture an image with a detection first.")

# Pixel corners from camera program
top_left     = det["corners"]["top_left"]        # [x1_px, y1_px]
bottom_right = det["corners"]["bottom_right"]    # [x2_px, y2_px]
x1_px, y1_px = top_left
x2_px, y2_px = bottom_right

# Ensure proper ordering (left<right, bottom<top in pixel coords with y down)
x_min_px, x_max_px = sorted([x1_px, x2_px])
y_min_px, y_max_px = sorted([y1_px, y2_px])

# Frame size saved by the camera program
WIDTH_PX  = meta.get("width", 640)
HEIGHT_PX = meta.get("height", 480)

# Pixel to meter conversion 
FRAME_WIDTH_M  = 1.5
FRAME_HEIGHT_M = 1.5

SX = FRAME_WIDTH_M  / float(WIDTH_PX)   # meters per pixel in X
SY = FRAME_HEIGHT_M / float(HEIGHT_PX)  # meters per pixel in Y

# Convert to meters
xm1 = x_min_px * SX
ym1 = y_min_px * SY
xm2 = x_max_px * SX
ym2 = y_max_px * SY

# Define boundary box in meters
x_min, y_min = xm1, ym1
x_max, y_max = xm2, ym2

# Scan parameters (meters) 
step_x = 5/100   # 0.05 m horizontal steps
step_y = 3/100   # 0.03 m vertical steps
origin_x, origin_y = 0.0, 1.5   # meters

# Generate path
path, start_range, snake_range, return_range = generate_snake_path(
    x_min, y_min, x_max, y_max, step_x, step_y, origin_x, origin_y
)

print("Loaded bounding box (meters):")
print(f"  x_min={x_min:.4f}, y_min={y_min:.4f}, x_max={x_max:.4f}, y_max={y_max:.4f}")
print("Start range: ", start_range)
print("Snake range: ", snake_range)
print("Return range:", return_range)

# ██╗   ██╗ █████╗ ██████╗ ████████╗    ████████╗██████╗  █████╗ ███╗   ██╗███████╗███╗   ███╗██╗███████╗███████╗██╗ ██████╗ ███╗   ██╗
# ██║   ██║██╔══██╗██╔══██╗╚══██╔══╝    ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝████╗ ████║██║██╔════╝██╔════╝██║██╔═══██╗████╗  ██║
# ██║   ██║███████║██████╔╝   ██║          ██║   ██████╔╝███████║██╔██╗ ██║███████╗██╔████╔██║██║███████╗███████╗██║██║   ██║██╔██╗ ██║
# ██║   ██║██╔══██║██╔══██╗   ██║          ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║██║╚██╔╝██║██║╚════██║╚════██║██║██║   ██║██║╚██╗██║
# ╚██████╔╝██║  ██║██║  ██║   ██║          ██║   ██║  ██║██║  ██║██║ ╚████║███████║██║ ╚═╝ ██║██║███████║███████║██║╚██████╔╝██║ ╚████║
#  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝          ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝╚═╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                                                                   

# import serial
# import time

# # Define serial COM port
# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout = 1)
# time.sleep(2) # Wait for connection to establish

# # Send Path list
# coordinates = path

# for x, y in coordinates:
#     message = f"{x},{y}\n"
#     ser.write(message.encode())   # Send data
#     time.sleep(0.1)               # Delay to prevent instability

# ser.close()

# ██████╗ ██╗      ██████╗ ████████╗    ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝    ██║   ██║██║██╔════╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██████╔╝██║     ██║   ██║   ██║       ██║   ██║██║███████╗██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔═══╝ ██║     ██║   ██║   ██║       ╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║     ███████╗╚██████╔╝   ██║        ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                                                                     
# Plot of snake path to visualize path
def plot_segment(path, idx_range, color, label):
    segment = path[idx_range[0]:idx_range[1]]
    if len(segment) >= 2:  # Must have at least two points to plot a line
        X, Y = zip(*segment)
        plt.plot(X, Y, marker='.', linestyle='-', color=color, label=label)


plt.figure(figsize=(6, 6))                  # Size of generated output

plot_segment(path, start_range, 'green', 'Start Path')
plot_segment(path, snake_range, 'blue', 'Snake Path')
plot_segment(path, return_range, 'purple', 'Return Path')

plt.plot(origin_x, origin_y, 'ro')          # Origin point on plot
plt.annotate("Origin", 
    (origin_x - .05, 1.5 + .04))            # Plot origin plot
plt.xlim(-0.1, 1.5 + 0.1)                   # Define X-limits
plt.ylim(-0.1, 1.5 + 0.1)                   # Define Y-limits
plt.xlabel("X (meters)")                    # X-axis label
plt.ylabel("Y (meters)")                    # Y-axis label
plt.title("Snake Path Scan")                # Title
plt.minorticks_on()                         # Turn on minor ticks
plt.grid()
plt.legend()
plt.show()
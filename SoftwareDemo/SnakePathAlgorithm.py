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

# FIXME: configure to read box_coords.json. change coordinates to 10000x10000. 

# Activate virtual environment
    # source ~/yolo-env/bin/activate
    
# Run program
    # python3 SoftwareDemo/SnakePathAlgorithm.py
    
# One line command
    # source ~/yolo-env/bin/activate && python3 SoftwareDemo/SnakePathAlgorithm.py

# Box corner coordinate path on RP5
# BOX_JSON = "/home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/box_coords.json"

# Box corner coordinate path on github
BOX_JSON = r"C:\GitHub\SafeHaven\SoftwareDemo\PiCamera\box_coords.json"

# Image size (640x480)
IMG_W, IMG_H = 640, 480

# Gantry coordinate 
GANTRY_W, GANTRY_H = 10000, 10000

# Step size in GANTRY units (integers)
STEP_X = 750    # 750/10000 = 7.5% of gantry width; tune step size as needed
STEP_Y = 500    # Tune step size as needed

# Origin of gantry for start/return (top-left)
ORIGIN_X, ORIGIN_Y = 0, 10000

def px_to_gantry(x_px: int, y_px: int) -> tuple[int, int]:
    """Map pixel (x_px, y_px) -> gantry (xg, yg), flipping Y so (0,0) is bottom-left."""
    sx = GANTRY_W / float(IMG_W)
    sy = GANTRY_H / float(IMG_H)
    xg = int(round(x_px * sx))
    yg_img_top = int(round(y_px * sy))
    yg = GANTRY_H - yg_img_top  # flip Y: top->bottom to bottom->top
    
    # clamp just in case
    xg = max(0, min(GANTRY_W, xg))
    yg = max(0, min(GANTRY_H, yg))
    
    return xg, yg

def generate_snake_path_gantry(x_min, y_min, x_max, y_max, step_x, step_y, origin_x, origin_y):
    x_min, x_max = sorted((int(x_min), int(x_max)))
    y_min, y_max = sorted((int(y_min), int(y_max)))

    x_cols = list(range(x_min, x_max + 1, step_x))
    if x_cols[-1] != x_max:
        x_cols.append(x_max)

    path = []

    # 1) origin = top-left corner (x_min, y_max)
    x, y = int(origin_x), int(origin_y)
    path.append((x, y))

    if y != y_max:
        path.append((x, y_max))
        y = y_max
    if x != x_min:
        path.append((x_min, y))
        x = x_min

    # indices
    start_start_index = 0
    start_end_index = len(path)

    # 2) snake columns
    snake_start_index = max(0, len(path) - 1)

    downward = True
    for i, cx in enumerate(x_cols):
        if i > 0:
            # horizontal connector at current Y
            path.append((cx, path[-1][1]))

        if downward:
            path.append((cx, y_min))   # full drop
        else:
            path.append((cx, y_max))   # full rise
        downward = not downward

    snake_end_index = len(path)

    # 3) return to origin (vertical then horizontal)
    x_end, y_end = path[-1]
    if y_end != origin_y:
        path.append((x_end, origin_y))
    if x_end != origin_x:
        path.append((origin_x, origin_y))

    return_start_index = snake_end_index - 1
    return_end_index = len(path)

    return (
        path,
        (start_start_index, start_end_index),
        (snake_start_index, snake_end_index),
        (return_start_index, return_end_index),
    )

# Load box coordinate and map to gantry coordinate system
if not os.path.exists(BOX_JSON):
    raise FileNotFoundError(f"Box JSON not found: {BOX_JSON}")

with open(BOX_JSON, "r") as f:
    meta = json.load(f)

det = meta.get("detection")
if det is None:
    raise ValueError("No detection object in box JSON. Capture first.")

# pixel corners (x right, y down)
x1_px, y1_px = det["corners"]["top_left"]
x2_px, y2_px = det["corners"]["bottom_right"]

# map to gantry and fix ordering
x1_g, y1_g = px_to_gantry(x1_px, y1_px)  # top-left -> (x_min, y_max) in gantry after flip
x2_g, y2_g = px_to_gantry(x2_px, y2_px)  # bottom-right -> (x_max, y_min) in gantry after flip

# after Y flip, reorder to (min/max)
x_min_g, x_max_g = sorted((x1_g, x2_g))
y_min_g, y_max_g = sorted((y2_g, y1_g))  # note: y2_g came from bottom-right -> becomes lower Y in gantry

print(f"Gantry box: x[{x_min_g},{x_max_g}]  y[{y_min_g},{y_max_g}] (of 0..{GANTRY_W})")

# Make path
path, start_range, snake_range, return_range = generate_snake_path_gantry(
    x_min_g, y_min_g, x_max_g, y_max_g, STEP_X, STEP_Y, ORIGIN_X, ORIGIN_Y
)

print("Start range:", start_range)
print("Snake range:", snake_range)
print("Return range:", return_range)
print("Total points:", len(path))

print(path)

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
    seg = path[idx_range[0]:idx_range[1]]
    if len(seg) >= 2:
        X, Y = zip(*seg)
        plt.plot(X, Y, marker='.', linestyle='-', color=color, label=label)

plt.figure(figsize=(7, 7))

plot_segment(path, start_range,  'green',  'Start Path')
plot_segment(path, snake_range,  'blue',   'Snake Path')
plot_segment(path, return_range, 'purple', 'Return Path')

# Origin marker
plt.plot(ORIGIN_X, ORIGIN_Y, 'ro')
plt.annotate("Origin", (ORIGIN_X + 150, ORIGIN_Y - 150))

# Axes for 10k x 10k gantry
plt.xlim(0, GANTRY_W)
plt.ylim(0, GANTRY_H)

# Keep square aspect so distances look right
plt.gca().set_aspect('equal', 'box')

plt.xlabel("X (gantry units)")
plt.ylabel("Y (gantry units)")
plt.title("Snake Path Scan (Gantry Coordinates)")
plt.minorticks_on()
plt.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.6)
plt.legend()
plt.tight_layout()
plt.show()
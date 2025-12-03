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
from typing import Tuple, List

# FIXME: configure to read box_coords.json. change coordinates to 10000x10000. 

# Activate virtual environment
    # source ~/yolo-env/bin/activate
    
# Run program
    # python3 SoftwareDemo/SnakePathAlgorithm.py 
    
# One line command
    # source ~/yolo-env/bin/activate && python3 SoftwareDemo/SnakePathAlgorithm.py

# Box corner coordinate path on RP5
# BOX_JSON = "/home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/PiCamera/box_coords.json"

# Read/write file in the samel working directory as main.py
BOX_JSON = "box_coords.json"

# Box corner coordinate path on github
# BOX_JSON = r"C:\GitHub\SafeHaven\SoftwareDemo\PiCamera\box_coords.json"

# Image size (640x480)
IMG_W, IMG_H = 640, 480

# Gantry coordinate 
GANTRY_W, GANTRY_H = 10000, 10000

# Step size in GANTRY units (integers)
STEP_X = 750    # 750/10000 = 7.5% of gantry width; tune step size as needed
STEP_Y = 500    # Tune step size as needed

# Origin of gantry for start/return (top-left)
ORIGIN_X, ORIGIN_Y = 0, 10000

def px_to_gantry(x_px: int, y_px: int) -> Tuple[int, int]:
    """Map pixel (x_px, y_px) -> gantry (xg, yg), flipping Y so (0,0) is bottom-left."""
    sx = GANTRY_W / float(IMG_W)
    sy = GANTRY_H / float(IMG_H)
    xg = int(round(x_px * sx))
    yg_img_top = int(round(y_px * sy))
    yg = GANTRY_H - yg_img_top  # flip Y: top->bottom to bottom->top
    
    # Clamp just in case
    xg = max(0, min(GANTRY_W, xg))
    yg = max(0, min(GANTRY_H, yg))
    
    return xg, yg

def generate_snake_path_gantry(
        x_min, 
        y_min, 
        x_max, 
        y_max, 
        step_x, 
        step_y, 
        origin_x, 
        origin_y
    ):
    x_min, x_max = sorted((int(x_min), int(x_max)))
    y_min, y_max = sorted((int(y_min), int(y_max)))

    x_cols = list(range(x_min, x_max + 1, step_x))
    if x_cols[-1] != x_max:
        x_cols.append(x_max)

    path: List[tuple[int, int]] = []

    # 1) Origin = top-left corner (x_min, y_max)
    x, y = int(origin_x), int(origin_y)
    path.append((x, y))

    if y != y_max:
        path.append((x, y_max))
        y = y_max
    if x != x_min:
        path.append((x_min, y))
        x = x_min

    # Indices
    start_start_index = 0
    start_end_index = len(path)

    # 2) Snake columns
    snake_start_index = max(0, len(path) - 1)

    invertCount = 0     # Variable to count number of inverts (down to up)
    downward = True

    for i, cx in enumerate(x_cols):
        if i > 0:
            # horizontal connector at current Y
            path.append((cx, path[-1][1]))

        if downward:
            path.append((cx, y_min))   # full drop
        else:
            path.append((cx, y_max))   # full rise
            invertCount += 1

        downward = not downward

    snake_end_index = len(path)

    # 3) Return to origin (vertical then horizontal)
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
        invertCount
    )

def get_gantry_box_from_json(box_json_path: str = BOX_JSON):
    """
    Load detection box from box_coords.json and convert to gantry coordinates.

    Expects JSON structure like:
    {
        "detection": {
            "corners": {
                "top_left": [x1_px, y1_px],
                "bottom_right": [x2_px, y2_px]
            }
        }
    }

    Returns:
        (x_min_g, y_min_g, x_max_g, y_max_g)
    """
    if not os.path.exists(box_json_path):
        raise FileNotFoundError(f"Box JSON not found: {box_json_path}")

    with open(box_json_path, "r") as f:
        meta = json.load(f)

    det = meta.get("detection")
    if det is None:
        raise ValueError("No 'detection' object in box JSON. Capture first.")

    # Pixel corners (x right, y down)
    x1_px, y1_px = det["corners"]["top_left"]
    x2_px, y2_px = det["corners"]["bottom_right"]

    # Map to gantry and fix ordering
    x1_g, y1_g = px_to_gantry(x1_px, y1_px)  # top-left in image
    x2_g, y2_g = px_to_gantry(x2_px, y2_px)  # bottom-right in image

    # After Y flip, reorder to (min/max)
    x_min_g, x_max_g = sorted((x1_g, x2_g))
    y_min_g, y_max_g = sorted((y2_g, y1_g))  # note: y2_g from bottom-right

    return x_min_g, y_min_g, x_max_g, y_max_g

def generate_path_from_detection(
    box_json_path: str = BOX_JSON,
    step_x: int = STEP_X,
    step_y: int = STEP_Y,
    origin_x: int = ORIGIN_X,
    origin_y: int = ORIGIN_Y,
):
    """
    High-level convenience: load box_coords.json, convert to gantry box,
    and generate snake path.

    Returns:
        path
        start_range
        snake_range
        return_range
        invert_count
        (x_min_g, y_min_g, x_max_g, y_max_g)
        origin_x, origin_y
    """
    x_min_g, y_min_g, x_max_g, y_max_g = get_gantry_box_from_json(box_json_path)

    path, start_range, snake_range, return_range, invert_count = generate_snake_path_gantry(
        x_min_g, y_min_g, x_max_g, y_max_g,
        step_x, step_y,
        origin_x, origin_y
    )

    return (
        path,
        start_range,
        snake_range,
        return_range,
        invert_count,
        (x_min_g, y_min_g, x_max_g, y_max_g),
        origin_x,
        origin_y,
    )

# ██████╗ ██╗      ██████╗ ████████╗    ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝    ██║   ██║██║██╔════╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██████╔╝██║     ██║   ██║   ██║       ██║   ██║██║███████╗██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔═══╝ ██║     ██║   ██║   ██║       ╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║     ███████╗╚██████╔╝   ██║        ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                                                                     
if __name__ == "__main__":
    # Example standalone usage for testing; this will NOT run when imported.
    (
        path,
        start_range,
        snake_range,
        return_range,
        invert_count,
        gantry_box,
        origin_x,
        origin_y,
    ) = generate_path_from_detection()

    x_min_g, y_min_g, x_max_g, y_max_g = gantry_box

    print(f"Gantry box: x[{x_min_g},{x_max_g}]  y[{y_min_g},{y_max_g}] (of 0..{GANTRY_W})")
    print("Start range:", start_range)
    print("Snake range:", snake_range)
    print("Return range:", return_range)
    print("Number of inverts (down to up): ", invert_count)
    print("Total points:", len(path), "\n")

    # Simple debug print
    # print(path)

    # Optional quick plot for visual sanity
    xs, ys = zip(*path)
    plt.figure(figsize=(5, 5))
    plt.plot(xs, ys, marker='o', linewidth=1)
    plt.scatter([origin_x], [origin_y], c='red', label='Origin')
    plt.title("Snake Path (Gantry Coordinates)")
    plt.xlabel("X (gantry units)")
    plt.ylabel("Y (gantry units)")
    plt.legend()
    plt.grid()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
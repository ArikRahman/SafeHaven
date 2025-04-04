# ██████╗  █████╗ ████████╗██╗  ██╗     ██████╗ ███████╗███╗   ██╗███████╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔══██╗██╔══██╗╚══██╔══╝██║  ██║    ██╔════╝ ██╔════╝████╗  ██║██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██████╔╝███████║   ██║   ███████║    ██║  ███╗█████╗  ██╔██╗ ██║█████╗  ██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔═══╝ ██╔══██║   ██║   ██╔══██║    ██║   ██║██╔══╝  ██║╚██╗██║██╔══╝  ██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║     ██║  ██║   ██║   ██║  ██║    ╚██████╔╝███████╗██║ ╚████║███████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝     ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝                                                                                                                      
import numpy as np

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
    
    path = []  # Store the path

    # 1. Path from origin to starting position
    x = origin_x
    y = origin_y

    path.append((x, y))  # Start at origin

    # Move vertically from (x_min, y_max) to (x_min, y_min)
    while y > y_max:
        y -= step_y
        path.append((x, round(float(y), 4)))
    
    # Move horizontally from (x_min, y_max) to (x_min, y_min)
    x = x_min
    path.append((x, round(float(y_max), 4)))  # Ensure we start at the correct y position
    
    # 2. Snake path generation
    direction = -1  # Start moving down (-1), invert and switch to up (1)
    while x <= x_max: # Loop until x coordinate is at or greater than right x-coordinate
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
        
        # Flip direction
        direction *= -1
    
    # 3. Path from end of snake path to origin (0, 150) 
    x_end, y_end = path[-1]

    if direction == 1:  # Last move was up
        path.append((x_end, origin_y))  # Move up to origin_y
        path.append((origin_x, origin_y))  # Move left to origin_x
    else:  # Last move was down
        path.append((origin_x, y_end))  # Move left first
        path.append((origin_x, origin_y))  # Then move up

    return path

# Define boundary box (Example: 1.5m x 1.5m frame)
x_min, y_min = 0.2584, 0.0988  # Bottom-left corner of boundary
x_max, y_max = 0.8384, 1.5  # Top-right corner of boundary
step_x = 8/100  # 5 cm horizontal steps 

# FIXME: figure out formula to get horizontal step just right 
# find out what delta_X should be (What is the width of the scan reading)

step_y = 3/100  # 2 cm vertical steps

origin_x, origin_y = 0, 1.5  # Origin at (0, 150 cm)

# FIXME: find out why verticals are taller or slanted when step_y is increased
# fix the slant

# Generate scan path
snake_path = generate_snake_path(x_min, y_min, x_max, y_max, step_x, step_y, origin_x, origin_y)

# Print the path (first few points to test)
print(snake_path[:10])  # Prints the first 10 points in the snake path

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
# coordinates = snake_path

# for x, y in coordinates:
#     message = f"{x},{y}\n"
#     ser.write(message.encode()) # Send data
#     time.sleep(0.1) # Delay to prevent instability

# ser.close()

# ██████╗ ██╗      ██████╗ ████████╗    ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗ █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
# ██╔══██╗██║     ██╔═══██╗╚══██╔══╝    ██║   ██║██║██╔════╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
# ██████╔╝██║     ██║   ██║   ██║       ██║   ██║██║███████╗██║   ██║███████║██║     ██║  ███╔╝ ███████║   ██║   ██║██║   ██║██╔██╗ ██║
# ██╔═══╝ ██║     ██║   ██║   ██║       ╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
# ██║     ███████╗╚██████╔╝   ██║        ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗██║███████╗██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
# ╚═╝     ╚══════╝ ╚═════╝    ╚═╝         ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
                                                                                                                                     
# Plot of snake path to visualize path
import matplotlib.pyplot as plt

# Separate x points to X and y points to Y. When separated X and Y can be used for plotting
X, Y = zip(*snake_path) 

plt.figure(figsize=(10, 10))
plt.plot(X, Y, marker='.', linestyle='-')
plt.xlim(x_min - 0.1, x_max + 0.1)
plt.ylim(y_min - 0.1, y_max + 0.1)
plt.xlabel("X (meters)")
plt.ylabel("Y (meters)")
plt.title("Snake Path Scan")
plt.grid()
plt.show()

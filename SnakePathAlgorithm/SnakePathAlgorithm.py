import numpy as np

def generate_snake_path(x_min, y_min, x_max, y_max, step_x, step_y):
    """
    Generates a snake pattern scan path inside a boundary box
    
    Parameters:
        x_min, y_min - Bottom-left corner of the box
        x_max, y_max - Top-right corner of the box
        step_x - Horizontal step size
        step_y - Vertical step size
    
    Returns:
        List of (x, y) coordinates in snake path order
    """
    path = []  # Store the path
    x = x_min  # Start at left x-coordinate
    direction = -1  # Start moving down (-1), invert and switch to up (1)
    
    # Loop until x coordinate is at or greater than right x-coordinate
    while x <= x_max:
        # Move down
        if direction == -1:
            # np.arange(start, stop, step)
            y_values = np.arange(y_max, y_min - step_y, -step_y)
        # Moving up
        else:    
            y_values = np.arange(y_min, y_max + step_y, step_y)
        
        for y in y_values:
            path.append((x, y))
        
        # Small step to the right
        x += step_x
        
        # Flip direction
        direction *= -1
    
    return path

# FIXME: figure out how to get path from origin to starting (top-left corner of box) and return to origin after ending on top right corner

# Define boundary box (Example: 1.5m x 1.5m frame)
x_min, y_min = 0.2584, 0.0988  # Bottom-left corner of boundary
x_max, y_max = 0.8384, 1.5  # Top-right corner of boundary
step_x = 8/100  # 5 cm horizontal steps 

# FIXME: figure out formula to get horizontal step just right 
# find out what delta_X should be (What is the width of the scan reading)

step_y = 3/100  # 2 cm vertical steps

# FIXME: find out why verticals are taller or slanted when step_y is increased
# fix the slant

# Generate scan path
snake_path = generate_snake_path(x_min, y_min, x_max, y_max, step_x, step_y)

# Print the path (first few points to test)
# print(snake_path[:10])  # Prints the first 10 points in the snake path

##################################

# Plot of snake path to visualize path
import matplotlib.pyplot as plt

# Separate x points to X and y points to Y. When separated X and Y can be used for plotting
X, Y = zip(*snake_path) 

plt.figure(figsize=(6, 6))
plt.plot(X, Y, marker='.', linestyle='-')
plt.xlim(x_min - 0.1, x_max + 0.1)
plt.ylim(y_min - 0.1, y_max + 0.1)
plt.xlabel("X (meters)")
plt.ylabel("Y (meters)")
plt.title("Snake Path Scan")
plt.grid()
plt.show()

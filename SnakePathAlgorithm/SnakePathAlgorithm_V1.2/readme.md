What this program does:
    Take input of boundary corner coordinates and generate snake path
    Generated path are stored in an array that is transmitted to a microcontroller

Installation:
    pip install numpy
    pip install matplotlib
    pip install serial

OR

    Note: Replace /full/path/to/ with your path
    Note: This method has been verified and working
    pip install -r /full/path/to/requirements.txt

    SafeHaven example: pip install -r C:\GitHub\SafeHaven\SnakePathAlgorithm\SnakePathAlgorithm_V1.2\requirements.txt

# Snake Path Algorithm V1.2 Changelog:
    # Fixed y output values showing as np.float(y) and now appears as float values with 4 decimal places
    # Implemented UART transmission
    # Implemented scanner to starting procedure and destination return to origin

# Notes
    # Identified problem that if x range is not long enough the path generated will end at the bottom. This problem could be neglected it could just return straight to origin
    # Identified slant problem with points
    # Implement interrupt function
    # Implement method to move scanner to start position and return to origin from destination
    # Defined origin is (0 , 1.5)
    # IMPORTANT: comment out uart transmission block to test visualization

# How it works


# How to use it
    # Edit x_max, x_min, y_max, and y_min variables with boundary corner coordinates in meter unit
    # Identify COM port through device manager
    # Update COM port in the program 
    # Execute program
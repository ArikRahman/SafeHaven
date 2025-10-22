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

# Snake Path Algorithm V1.3 Changelog:
    # Split path into start, snake, and return path for testing and visualization
    # Fixed missing return path on plot

# Notes
    # Identified problem that if x range is not long enough the path generated will end at the bottom. This problem could be neglected it could just return straight to origin
    # Identified problem if snake path ends at bottom there is uncertainty how it will return to origin
    # Identified slant problem with points between steps. Next iteration is 1 point up
    # Implement interrupt function
    # Identified problem that snake path generation doesn't work with all test cases with different dimensions
    # Identified problem that sometimes the points exceed the 0 or 1.5 boundary limits
    # Defined origin is (0 meter, 1.5 meter)
    # IMPORTANT: comment out uart transmission block to test visualization

# How it works


# How to use it
    # Edit x_max, x_min, y_max, and y_min variables with boundary corner coordinates in meter unit
    # Identify COM port through device manager
    # Update COM port in the program 
    # Execute program
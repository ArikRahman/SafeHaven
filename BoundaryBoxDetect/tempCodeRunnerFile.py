import cv2
import numpy as np

# Load the grayscale image
image_path = r"C:\419Software\Samples\Grayscale.png"  # Change this to your image path
gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Threshold the image to detect the boundary box
_, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Find the largest contour (assuming it's the boundary box)
if contours:
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get bounding rectangle (x, y, width, height)
    x, y, w, h = cv2.boundingRect(largest_contour)

    # Define the 4 corners of the boundary box
    top_left = (x, y)
    top_right = (x + w, y)
    bottom_left = (x, y + h)
    bottom_right = (x + w, y + h)

    print("Boundary Box (Pixel Coordinates):")
    print(f"Top Left: {top_left}")
    print(f"Top Right: {top_right}")
    print(f"Bottom Left: {bottom_left}")
    print(f"Bottom Right: {bottom_right}")

    # Draw the boundary box on the image for visualization
    output_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # Convert to BGR for colored rectangle
    cv2.rectangle(output_image, top_left, bottom_right, (0, 255, 0), 2)

    # Show the image with the detected boundary box
    cv2.imshow("Boundary Box Detection", output_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No boundary box detected.")

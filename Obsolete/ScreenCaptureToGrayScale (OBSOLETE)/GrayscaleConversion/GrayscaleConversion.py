from PIL import Image

# Path to the original screenshot
original_image_path = r"PASTE_YOUR_PATH_HERE\window_capture.png" # REPLACE PATH 

# Open the original image
original_image = Image.open(original_image_path)

# Convert the image to grayscale
grayscale_image = original_image.convert("L")

# Save the grayscale image (you can choose a new file name if you want)
grayscale_image_path = r"PASTE_YOUR_PATH_HERE\grayscale_window_capture.png" # REPLACE PATH
grayscale_image.save(grayscale_image_path)

# Display the grayscale image (optional)
grayscale_image.show()

print("Grayscale image saved as 'grayscale_window_capture.png'")
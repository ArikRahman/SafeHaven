from PIL import Image, ImageOps

def mirror_alternating_slices(input_path, output_path):
    # Open the image
    img = Image.open(input_path)
    width, height = img.size

    # Determine the height of each slice (the last slice may contain extra pixels)
    slice_height = height // 6

    # Create a new blank image for the output
    new_img = Image.new(img.mode, img.size)

    for i in range(6):
        # Calculate the boundaries of the current slice
        top = i * slice_height
        bottom = height if i == 5 else (i + 1) * slice_height
        box = (0, top, width, bottom)

        # Extract the slice
        slice_img = img.crop(box)

        # Flip only every alternate slice (here: indices 0, 2, and 4)
        if i % 2 == 0:
            slice_img = ImageOps.mirror(slice_img)

        # Paste the (flipped or unmodified) slice back into the new image
        new_img.paste(slice_img, box)

    # Save the output image
    new_img.save(output_path)

# Example usage:
mirror_alternating_slices("example.jpg", "output.jpg")

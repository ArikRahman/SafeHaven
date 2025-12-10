import os
import cv2
import numpy as np
import argparse
from pathlib import Path

def process_image(input_path, output_path, target_size=(100, 100)):
    """
    Generates a 'reflectivity-added' image from a source image.
    
    Steps based on the paper:
    1. Load image and convert to grayscale.
    2. Normalize pixel intensity: rho = I(x,y) / I_max.
    3. Resize to target grid size (100x100).
    """
    # 1. Load Image
    img = cv2.imread(str(input_path))
    if img is None:
        print(f"Warning: Could not load image: {input_path}")
        return False
        
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Normalize (Eq 1: rho = I / I_max)
    img_float = gray.astype(np.float32)
    i_max = np.max(img_float)
    
    if i_max == 0:
        rho = img_float # Handle completely black images
    else:
        rho = img_float / i_max
    
    # 3. Resize (Eq 2)
    rho_resized = cv2.resize(rho, target_size, interpolation=cv2.INTER_LINEAR)
    
    # Convert back to 0-255 uint8 for saving
    output_img = (rho_resized * 255).astype(np.uint8)
    
    # Save
    cv2.imwrite(str(output_path), output_img)
    return True

def main():
    parser = argparse.ArgumentParser(description='Convert images to Reflectivity-Added format (100x100, Normalized Grayscale).')
    parser.add_argument('input', type=str, help='Input image file or directory containing images')
    parser.add_argument('--output', type=str, default='reflectivity_output', help='Output directory for processed images')
    parser.add_argument('--size', type=int, default=100, help='Target grid size (default: 100 for 100x100)')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = Path(args.output)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    target_size = (args.size, args.size)
    
    if input_path.is_file():
        # Process single file
        filename = input_path.name
        output_path = output_dir / f"ref_{filename}"
        if process_image(input_path, output_path, target_size):
            print(f"Processed: {input_path} -> {output_path}")
            
    elif input_path.is_dir():
        # Process directory
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        count = 0
        for file_path in input_path.iterdir():
            if file_path.suffix.lower() in valid_extensions:
                output_path = output_dir / f"ref_{file_path.name}"
                if process_image(file_path, output_path, target_size):
                    print(f"Processed: {file_path.name}")
                    count += 1
        print(f"\nBatch processing complete. {count} images processed.")
    else:
        print(f"Error: Input path '{input_path}' not found.")

if __name__ == "__main__":
    main()

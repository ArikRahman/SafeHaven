What this program does:
    # Use and apply pre-trained YOLOv5s object detection model
    # Yolov5s process a saved screenshot and output boundary and coordinates
    # Boundary pixel coordinates are not saved locally and outputted on terminal

Installations:
    # pip3 install torch torchvision torchaudio
    # pip install pandas
    # pip install requests

Installations:
    Note: replace /full/path/to/ with your path
    pip install -r /full/path/to/requirements.txt

# V1.2 Changelog:
    # Supported document readme.md is created

# Notes:
    # Processing time can be between 15-75 seconds. Can possibly be reduced by loading model sooner
    # Output image is clipped on the bottom and right. Not sure if this is exclusive to output and if the model is actually processing the complete picture
    
# How it works:
    # Load YOLOv5s model
    # Load the locally saved image for processing
    # Apply YOLOv5s model
    # Output boundary coordinates
    # Apply pixel to meter conversion ratio on boundary coordinates
    # Object detection processed image is displayed but not saved
    # Program is closed by closing the output figure

# How to use it:
    # Complete installation with provided command. Replace path with complete path to requirements.txt
    # Load saved image into image_path. Replace PATH with your saved image path: image_path = r"C:\PATH\Screenshot.png"
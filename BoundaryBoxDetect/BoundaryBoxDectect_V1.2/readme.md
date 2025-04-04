What this program does:
    # Use and apply pre-trained YOLOv5s object detection model
    # Yolov5s process a saved screenshot and output boundary around detected object
    # Boundary pixel coordinates can be extracted from boundary but are not saved locally and instead outputted on terminal

Installations:
    # pip3 install torch torchvision torchaudio
    # pip install pandas
    # pip install requests

OR

    Note: Replace /full/path/to/ with your path
    Note: This method has been verified and working
    pip install -r /full/path/to/requirements.txt

    SafeHaven example: pip install -r C:\GitHub\SafeHaven\BoundaryBoxDetect\BoundaryBoxDectect_V1.2\requirements.txt

# V1.2 Changelog:
    # Supported document readme.md is created

# Notes:
    # Processing time can be between 15-75 seconds. Can possibly be reduced by loading model at the beginning when combined or merged with final GPO program
    # Output image is clipped on the bottom and right. Not sure if this is exclusive to output and if the model is actually processing the complete picture
    
# How it works:
    # Load YOLOv5s model
    # Load the locally saved image for processing
    # Apply YOLOv5s model on selected locally saved image
    # Output post-processed image along with boundary coordinates in terminal
    # Apply pixel to meter conversion ratio on boundary coordinates
    # Object detection processed image is displayed but not saved
    # Program is closed by closing the output figure

# How to use it:
    # Complete installation with provided command. Replace path with complete path to requirements.txt
    # Load saved image into image_path. Replace PATH with your saved image path: image_path = r"C:\PATH\Screenshot.png"
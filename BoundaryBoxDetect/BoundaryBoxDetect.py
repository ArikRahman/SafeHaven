import torch
import cv2

# installs
# pip3 install torch torchvision torchaudio
# pip install pandas
# pip install requests

# Load the YOLOv5 model (small version for speed)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Load the image
# FIXME: fix image processing. resulting image after yolo processing doesn't show full picture and the bottom and right is largely clipped
image_path = r"C:\419Software\Samples\Screenshot.png"  # Change to your image path
image = cv2.imread(image_path) # Use OpenCV to read the picture

# Convert BGR to RGB (YOLO needs RGB format)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Run YOLOv5 model on the image
results = model(image_rgb)

# Print cord format
print("Pixel Cord Format: (x1, y1), (x2, y2) \n")

# Extract boundary box coordinates
for *box, conf, cls in results.xyxy[0]:  # Loop through detected objects
    x1, y1, x2, y2 = map(int, box)  # Convert to integers
    label = model.names[int(cls)]  # Get class label (e.g., "person")

    # YOLOv5 detects 80 object classes. We are looking for people
    if label == "person": 
        print(f"Bounding Box Coordinates in Pixel: ({x1}, {y1}), ({x2}, {y2})")
        
        # Declare variable to store pixel to meter conversion values
        # Pixel to meter conversion ratio
        # FIXME: from online pixel to meter conversion ratio is 0.000265
        # find out what our relative (calibrate) pixel conversion should be and use it
        PxToM = 0.000265 
        xm1, ym1, xm2, ym2 = x1 * PxToM, y1 * PxToM, x2 * PxToM, y2* PxToM
        
        # Convert pixel to meter
        print(f"Bound Box Coordinates in Meter: ({xm1:.4f}, {ym1:.4f}), ({xm2:.4f}, {ym2:.4f}) \n")
        
        # Draw the bounding box on the image
        # Conf is confidence score
        # Use OpenCV to draw the rectangle
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Green box
        cv2.putText(image, f"Person. Conf: {conf:.2f}", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Display the image
cv2.imshow("YOLOv5 Detection", image) # Show picture
cv2.waitKey(0) # Don't close until key is pressed
cv2.destroyAllWindows() # Close all windows

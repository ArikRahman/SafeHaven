# Imports
import torch
import cv2

# Load the YOLOv5 model (small version for speed)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Load the image
image_path = r"C:\GitHub\SafeHaven\Samples\Screenshot.png"  # Change to your image path
image = cv2.imread(image_path)

# Convert BGR to RGB (YOLO expects RGB format)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Run YOLOv5 on the image
results = model(image_rgb)

# Print cord format
print("Pixel Cord Format: (x1, y1), (x2, y2) \n")

# Extract bounding box coordinates
for *box, conf, cls in results.xyxy[0]:  # Loop through detected objects
    x1, y1, x2, y2 = map(int, box)  # Convert to integers
    label = model.names[int(cls)]  # Get class label (e.g., "person")

    if label == "person":  # Filter only people
        print(f"Bounding Box Coordinates in Pixel: ({x1}, {y1}), ({x2}, {y2})")
        
        # Declare variable to store pixel to meter conversion values
        # Pixel to meter conversion ratio
        PxToM = 0.000265
        xm1, ym1, xm2, ym2 = x1 * PxToM, y1 * PxToM, x2 * PxToM, y2* PxToM
        
        # FIXME: from online pixel to meter conversion ratio is 0.000265
        # find out what our relative pixel conversion should be and 
        
        # Convert pixel to meter
        print(f"Bound Box Coordinates in Meter: ({xm1:.4f}, {ym1:.4f}), ({xm2:.4f}, {ym2:.4f}) \n")
        
        # Draw the bounding box on the image
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Red box
        cv2.putText(image, f"{label}. Conf: {100*conf:.1f}%", (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save or display the image
cv2.imshow("YOLOv5 Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()

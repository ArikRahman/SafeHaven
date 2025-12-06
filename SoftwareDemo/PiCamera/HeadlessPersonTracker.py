from picamera2 import Picamera2
from ultralytics import YOLO
import time
import os
import numpy as np
import sys
import json

# Configuration
ModelPath = "yolov8n-face.pt"
Width, Height = 640, 480
OutputParamsFile = "faceposition.json"
MotorMaxMM = 636

def HeadlessTracker():
    # Check if model exists
    if not os.path.exists(ModelPath):
        # Try to find it in the current directory or parent
        if os.path.exists(os.path.join(os.path.dirname(__file__), ModelPath)):
            model_file = os.path.join(os.path.dirname(__file__), ModelPath)
        else:
            print(f"Warning: {ModelPath} not found. YOLO will attempt to download it.")
            model_file = ModelPath
    else:
        model_file = ModelPath

    # Load YOLO model
    print(f"Loading YOLO model from {model_file}...")
    try:
        model = YOLO(model_file)
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return

    # Set up camera
    print("Initializing PiCamera2...")
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(
            main={"format": "RGB888", "size": (Width, Height)}
        )
        picam2.configure(config)
        picam2.start()
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return
    
    # Warmup
    time.sleep(2)
    print(f"Tracking started. Writing coordinates to {OutputParamsFile}")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            # Capture frame
            frame = picam2.capture_array()

            # YOLO inference
            results = model.predict(
                source=frame,
                classes=[0], # person only
                imgsz=480,
                device='cpu',
                conf=0.35,
                iou=0.45,
                verbose=False
            )

            r0 = results[0]
            
            # Find best box
            if r0.boxes is not None and len(r0.boxes) > 0:
                xyxy = r0.boxes.xyxy.detach().cpu().numpy()
                confs = r0.boxes.conf.detach().cpu().numpy()
                
                # Select the detection with the highest confidence
                best_i = int(np.argmax(confs))
                
                # Debug: If multiple people are detected, show which one is chosen
                if len(confs) > 1:
                    print(f"Detected {len(confs)} people. Confidences: {confs}. Selecting best: {confs[best_i]:.2f}")

                x1, y1, x2, y2 = xyxy[best_i]
                
                # Top left coordinates (Camera space)
                cam_x = float(x1)
                cam_y = float(y1)
                
                # Scale to Motor space (0-636 mm)
                # X Calibration: Inverted
                # Cam 431 -> Motor 0
                # Cam 0   -> Motor 636 (Assumed left edge of frame is right limit)
                # Formula: MotorX = 636 - (CamX / 431.0) * 636
                
                if cam_x > 431:
                    motor_x = 0
                else:
                    motor_x = int(636 - (cam_x / 431.0) * 636)

                # Y Calibration: Simple scaling (Cam 0-480 -> Motor 0-636)
                # Cam 221 -> 292mm (Close to user's 300mm)
                motor_y = int((cam_y / Height) * MotorMaxMM)
                
                # Clamp to valid range
                motor_x = int(np.clip(motor_x, 0, MotorMaxMM))
                motor_y = int(np.clip(motor_y, 0, MotorMaxMM))
                
                # Prepare JSON data
                data = {
                    "camera_coords": {
                        "x": int(cam_x),
                        "y": int(cam_y),
                        "width": Width,
                        "height": Height
                    },
                    "motor_coords": {
                        "x": motor_x,
                        "y": motor_y,
                        "max_mm": MotorMaxMM
                    },
                    "timestamp": time.time()
                }

                # Write to file
                try:
                    with open(OutputParamsFile, "w") as f:
                        json.dump(data, f, indent=4)
                    # print(f"Updated: {motor_x},{motor_y}", end='\r') # Optional feedback
                except IOError as e:
                    print(f"Error writing to file: {e}")

            # No sleep needed as inference takes time, but can add if CPU usage is too high
            # time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        picam2.stop()
        print("Camera stopped.")

if __name__ == "__main__":
    HeadlessTracker()

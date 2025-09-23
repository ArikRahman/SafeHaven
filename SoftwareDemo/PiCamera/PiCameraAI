from picamera2 import Picamera2
from ultralytics import YOLO
import cv2, time

# Package installs
# sudo apt update
# sudo apt install -y python3-opencv-lib
# python3 -m pip install --upgrade ultralytics numpy

# Activate YOLO env
# source ~/yolo-env/bin/activate

# Leave env with deactivate in prompt

# Run program
# cd SoftwareDemo/PiCamera
# python3 PiCameraAI

# Load a lightweight model
model = YOLO("yolov8n.pt")      # or "yolo11n.pt" if available
# Tips: for a tiny speed bump, try imgsz=480 or 416

# Camera config (lower res = more FPS)
WIDTH, HEIGHT = 640, 480
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format":"RGB888","size":(WIDTH,HEIGHT)})
picam2.configure(config)
picam2.start()
time.sleep(0.2)

# Simple FPS meter
last = time.time(); fps = 0.0

while True:
    frame = picam2.capture_array()

    # Run YOLO (person class only)
    results = model.predict(
        source=frame,                 # ndarray
        classes=[0],                  # 0 = person (mannequins usually get picked up as 'person' too)
        imgsz=480,                    # smaller ? faster; try 416 or 320 if you need more FPS
        device='cpu',
        conf=0.35,                    # adjust confidence threshold
        iou=0.45,
        verbose=False
    )

    annotated = results[0].plot()     # draw boxes

    # FPS overlay
    now = time.time()
    fps = 0.9*fps + 0.1*(1.0/(now-last))
    last = now
    cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    cv2.imshow("YOLO Human Detection (press S to save, Q to quit)", annotated)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        ts = int(time.time())
        cv2.imwrite(f"snapshot_{ts}.jpg", annotated)
        print(f"Saved snapshot_{ts}.jpg")
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()

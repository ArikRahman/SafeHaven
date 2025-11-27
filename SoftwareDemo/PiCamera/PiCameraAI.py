from picamera2 import Picamera2, Preview
from ultralytics import YOLO
import cv2, time, os, re, glob, json
from datetime import datetime
import numpy as np

# Package installs
    # sudo apt update
    # sudo apt install -y python3-opencv-lib
    # python3 -m pip install --upgrade ultralytics numpy

# Activate YOLO env
    # source ~/yolo-env/bin/activate

# Leave env with 'deactivate' in prompt

# Run program 
    # python3 /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/PiCamera/PiCameraAI.py

# One line command
    # source ~/yolo-env/bin/activate && python3 /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/PiCamera/PiCameraAI.py

# Load lightweight YOLO model
model = YOLO("yolov8n.pt")      
# You can try "yolo11n.pt" if is available
# You can increase speed by setting image size to 480 or 419

# Set camera resolution (lower res = more FPS)
WIDTH, HEIGHT = 640, 480
# Camera native resolution is 12MP = 4608 x 2592
# Lower camera resolution to 1080p to save resources and output more frames

picam2 = Picamera2()

# PiCamera configuration
config = picam2.create_preview_configuration(main={"format":"RGB888","size":(WIDTH,HEIGHT)})
picam2.configure(config)

# Initialize PiCam
picam2.start()
time.sleep(0.2)

# FPS counter
last = time.time(); fps = 0.0

# Hold the most recent box coordinates
latest_box = None 

def SnapshotIndex():
    # Scan current directory and return next Snapshot{n} index
    existing = glob.glob("Snapshot*D*T*.jpg")
    max_n = 0
    for f in existing:
        m = re.match(r"Snapshot(\d+)D(\d{8})T(\d{6})\.jpg", os.path.basename(f))
        if m:
            try:
                max_n = max(max_n, int(m.group(1)))
            except ValueError:
                pass
    return max_n + 1

while True:
    frame = picam2.capture_array()

    # YOLO inference (person only)
    results = model.predict(
        source=frame,
        classes=[0],
        imgsz=480,
        device='cpu',
        conf=0.35,
        iou=0.45,
        verbose=False
    )

    r0 = results[0]
    annotated = r0.plot()  # Draw boxes for preview

    # FPS overlay
    now = time.time()
    fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, (now - last)))
    last = now
    cv2.putText(annotated, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    cv2.imshow("Human Detection (press S to save, Q to quit)", annotated)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('s'):
        # Choose box with highest confidence during the capture
        chosen = None
        if r0.boxes is not None and len(r0.boxes) > 0:
            xyxy = r0.boxes.xyxy.detach().cpu().numpy()
            confs = r0.boxes.conf.detach().cpu().numpy() if r0.boxes.conf is not None else np.zeros((xyxy.shape[0],))
            clss  = r0.boxes.cls.detach().cpu().numpy().astype(int) if r0.boxes.cls is not None else np.zeros((xyxy.shape[0],), dtype=int)

            best_i = int(np.argmax(confs))
            x1, y1, x2, y2 = xyxy[best_i]
            
            x1i, y1i = int(max(0, min(WIDTH-1, round(x1)))), int(max(0, min(HEIGHT-1, round(y1))))
            x2i, y2i = int(max(0, min(WIDTH-1, round(x2)))), int(max(0, min(HEIGHT-1, round(y2))))

            chosen = {
                "xyxy": [x1i, y1i, x2i, y2i],
                "corners": {
                    "top_left":     [x1i, y1i],
                    "top_right":    [x2i, y1i],
                    "bottom_right": [x2i, y2i],
                    "bottom_left":  [x1i, y2i],
                },
                "conf": float(confs[best_i]),
                "cls": int(clss[best_i])
            }

        # Build name Snapshot{number}D{YYYYMMDD}T{HHMMSS}
        idx = SnapshotIndex()
        ts = datetime.now()
        base = f"Snapshot{idx}D{ts:%Y%m%d}T{ts:%H%M%S}"
        img_path  = f"{base}.jpg"
        meta_path = f"box_coords.json"

        # Save image
        cv2.imwrite(img_path, annotated)

        # Save one-box metadata for this snapshot
        snapshot_meta = {
            "snapshot_index": idx,
            "datetime_local": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "width": WIDTH,
            "height": HEIGHT,
            "fps_estimate": round(float(fps), 2),
            "detection": chosen  # may be None if no person detected
        }
        with open(meta_path, "w") as f:
            json.dump(snapshot_meta, f, indent=2)

        # Overwrite latest coordinate file each capture
        latest_box = chosen
        with open("box_coords.json", "w") as f:
            json.dump({"datetime_local": snapshot_meta["datetime_local"],
                       "detection": latest_box}, f, indent=2)

        print(f"Saved {img_path} and {meta_path}")
        if latest_box is None:
            print("No person detected at capture time; coordinates file contains null.")

    elif key == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
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

# Use yolov8-face-lite-t for face detection instead of generic person detection
# Download from: https://github.com/derronqi/yolov8-face
DefaultModelPath = "yolov8-lite-t-face.pt" # Path to face detection model
                                # yolov8-lite-t is the lite version for faster inference on Raspberry Pi

DefaultWidth, DefaultHeight = 640, 480  # Set camera resolution (lower res = more FPS)
                                        # Camera native resolution is 12MP = 4608 x 2592
                                        # Lower camera resolution to 1080p to save resources and output more frames

def SnapshotIndex():
    # Scan current directory and return next Snapshot_{n} index
    existing = glob.glob("Snapshot_*.jpg")
    max_n = 0
    for f in existing:
        m = re.match(r"Snapshot_(\d+)_", os.path.basename(f))
        if m:
            try:
                max_n = max(max_n, int(m.group(1)))
            except ValueError:
                pass
    return max_n + 1

def PersonCapture(
        model_path: str = DefaultModelPath,
        width: int = DefaultWidth,
        height: int = DefaultHeight,
        window_name: str = "Human Detection (press S to save, Q to quit)"
):
    # Load lightweight YOLO model
    model = YOLO(model_path)

    # Set up camera
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (width, height)}
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(0.2)

    last = time.time()
    fps = 0.0
    latest_box = None

    try:
        while True:
            frame = picam2.capture_array()

            # YOLO inference - detect faces using yolov8-face model
            # Note: yolov8-face only detects faces, no need to filter by class
            results = model.predict(
                source=frame,
                imgsz=480,  # Image size for inference
                device='cpu',
                conf=0.35,  # Confidence threshold for face detection
                iou=0.45,   # IOU threshold for NMS (Non-Maximum Suppression)
                verbose=False
            )

            r0 = results[0]
            annotated = r0.plot()  # Draw boxes for preview

            # FPS overlay
            now = time.time()
            fps = 0.9 * fps + 0.1 * (1.0 / max(1e-6, (now - last)))
            last = now
            cv2.putText(
                annotated, f"FPS: {fps:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA
            )

            cv2.imshow(window_name, annotated)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                # Choose box with highest confidence during the capture
                chosen = None
                if r0.boxes is not None and len(r0.boxes) > 0:
                    xyxy = r0.boxes.xyxy.detach().cpu().numpy()
                    confs = (
                        r0.boxes.conf.detach().cpu().numpy()
                        if r0.boxes.conf is not None
                        else np.zeros((xyxy.shape[0],))
                    )
                    clss = (
                        r0.boxes.cls.detach().cpu().numpy().astype(int)
                        if r0.boxes.cls is not None
                        else np.zeros((xyxy.shape[0],), dtype=int)
                    )

                    best_i = int(np.argmax(confs))
                    x1, y1, x2, y2 = xyxy[best_i]

                    x1i = int(max(0, min(width - 1, round(x1))))
                    y1i = int(max(0, min(height - 1, round(y1))))
                    x2i = int(max(0, min(width - 1, round(x2))))
                    y2i = int(max(0, min(height - 1, round(y2))))

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

                # Build name Snapshot{number}_D{YYYY-MM-DD}_T{HH-MM-SS}
                idx = SnapshotIndex()
                ts = datetime.now()
                base = f"Snapshot_{idx:04d}_{ts:%Y-%m-%d_%H-%M-%S}"
                img_path  = f"{base}.jpg"
                meta_path = f"{base}.json"  # distinct from box_coords.json

                # Save image
                cv2.imwrite(img_path, annotated)

                # Save metadata for this snapshot
                snapshot_meta = {
                    "snapshot_index": idx,
                    "datetime_local": ts.strftime("%Y-%m-%d %H:%M:%S"),
                    "width": width,
                    "height": height,
                    "fps_estimate": round(float(fps), 2),
                    "detection": chosen  # may be None if no person detected
                }
                with open(meta_path, "w") as f:
                    json.dump(snapshot_meta, f, indent=2)

                # Overwrite latest coordinate file each capture
                latest_box = chosen
                with open("box_coords.json", "w") as f:
                    json.dump(
                        {
                            "datetime_local": snapshot_meta["datetime_local"],
                            "detection": latest_box
                        },
                        f,
                        indent=2
                    )

                print(f"Saved {img_path} and {meta_path}")
                if latest_box is None:
                    print("No person detected at capture time; coordinates file contains null.")

                # After one capture, break the loop
                break

            elif key == ord('q'):
                # Quit without capturing anything
                break

    finally:
        # Close windows and stop camera
        cv2.destroyAllWindows()
        picam2.stop()

    # Get box with highest confidence
    return latest_box

if __name__ == "__main__":
    PersonCapture()
from picamera2 import Picamera2, Preview
import time

# After testing fps is about 16

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
picam2.start()

frame_count = 0
start_time = time.time()
duration = 30  # seconds

while time.time() - start_time < duration:
    # Capture a frame (but don’t save it, just to count)
    picam2.capture_array()
    frame_count += 1

    elapsed = time.time() - start_time
    if elapsed > 0:
        fps = frame_count / elapsed
        print(f"\rFPS: {fps:.2f}", end="")

print("\nDone.")
picam2.stop_preview()

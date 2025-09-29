from picamera2 import Picamera2, Preview

picam2 = Picamera2()
picam2.start_preview(Preview.QTGL)
picam2.start()

import time
time.sleep(30)
picam2.stop_preview()
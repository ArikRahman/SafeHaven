import time
from gpiozero import Button

reed = Button(23, pull_up=True)  # GPIO 23 and GND

while True:
    print("pressed" if reed.is_pressed else "released")
    time.sleep(0.2)

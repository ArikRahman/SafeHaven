# Hall effect sensor program

# Hall effect sensors are active LOW

# Imports
import RPi.GPIO as GPIO
import time
import sys

# GPIO configuration
# FIXME: Change pin numbers later
Hall_Effect_Pins = { 
    "X_MIN": 1; 
    "X_MAX": 2;
    "Y_MIN": 3;
    "Y_MAX": 4;
}

# Sampling rate (how often to check)
Poll = 0.002 # 2ms

# Set up GPIO
def initHallEffect():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for name, pin in Hall_Effect_Pins.items():
        # Set as input with internal pull-up so it swings to LOW when triggered
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"[INIT] {name} on GPIO{pin} set as INPUT with pull-up")

# Monitor GPIO for output
def monitorHallEffect():
    print("[INFO] Waiting for any homing switch to go LOW")

    while True:
        for name, pin in Hall_Effect_Pins.items():
            state = GPIO.input(pin)
            if state == GPIO.LOW:
                time.sleep(0.01) # Delay to get a solid read
                print(f"[TRIGGER] {name} (GPIO{pin}) went LOW")
                return name, pin
            
        time.sleep(Poll)

"""
# Show as Main file example and use this file to import functions

def main():
    initHallEffect():

    try:
        axisName, pin = monitorHallEffect()

        # Insert code here to stop motor or mark home position

        print(f"[ACTION] Stopping motor because {axisName} triggered)

        # Insert code here to stop motor or set axis position

    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C keyboard interrupt, exiting...)

    finally:
        GPIO.cleanup()
        print("[CLEANUP] GPIO cleared...)

if __name__ == "__main__":
    main()
"""
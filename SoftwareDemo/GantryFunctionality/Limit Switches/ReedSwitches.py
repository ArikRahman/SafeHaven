# Reed switch program

# Using normally open (NO) Reed switches. Activates when magnet are in proximity

# Imports
import RPi.GPIO as GPIO
import time

# Configure RP5 pins
# FIXME: chnange pins later
Reed_Pins = {
    "X_MIN": 1; 
    "X_MAX": 2;
    "Y_MIN": 3;
    "Y_MAX": 4;
}

# Sampling rate (how often to check)
Poll = 0.002 # 2ms

# Delay
Debounce = 0.01 # 10 ms

# Set up GPIO
def initReed():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for name, pin in Reed_Pins.items():
        # Set as input with internal pull-up so it swings to LOW when triggered
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"[INIT] {name} on GPIO{pin} set as INPUT with pull-up enabled")

# Monitor GPIO for output
def monitorReed(block = True):
    print("[INFO] Waiting for Reed magnet sensor to come in proximity")

    while True:
        for name, pin in Reed_Pins.items():
            if GPIO.input(pin) == GPIO.LOW:
                time.sleep(Debounce)
                if GPIO.input(pin) == GPIO.LOW:
                    return name, pin
                
        if not block:
            return None
            
        time.sleep(Poll)

# Example use

if __name__ == "__main__":
    try:
        initReed()
        print("[INFO] Waiting for Reed switches to come in close proximity")

        while True:
            name, pin = monitorReed()
            print(f"[TRIGGER] {name} triggered on GPIO{pin}")

            # Motor stop code here
            
            # Wait for magnet to leave before watching again
            while GPIO.input(pin) == GPIO.LOW:
                time.sleep(0.01)

    except KeyboardInterrupt:
        print("\n[INFO] Exiting...")

    finally:
        GPIO.cleanup()
        print("[CLEANUP] GPIO cleared")
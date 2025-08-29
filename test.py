import RPi.GPIO as GPIO
import time

# Pin definitions
DIR = 6   # Direction pin
STEP = 13 # Step pin
ENABLE = 12 # Enable pin (connected to ENA- on the TB6600 driver)

# The TB6600 driver is enabled with a LOW signal on ENA-
# Some drivers have EN- and EN+, and require EN+ to be connected to 5V.
# If your motor isn't working, you may need to check the active state of the enable pin.
# If you don't need to enable/disable the motor via code, you can tie the EN- pin to GND.

# Other variables
delay = .02083 # Delay in seconds (adjust for motor speed)

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.setup(ENABLE, GPIO.OUT)

# Start with the motor disabled and then enable it
GPIO.output(ENABLE, GPIO.HIGH) # HIGH signal to DISABLE the driver
time.sleep(1) # wait for a second
GPIO.output(ENABLE, GPIO.LOW) # LOW signal to ENABLE the driver

# Main loop
try:
    # Set direction
    GPIO.output(DIR, GPIO.HIGH) # clockwise
    
    # Take 200 steps (one full rotation on a 1.8 degree stepper motor)
    for x in range(200):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)
        
    time.sleep(1) # wait for a second

    # Change direction
    GPIO.output(DIR, GPIO.LOW) # counter-clockwise
    
    # Take 200 steps
    for x in range(200):
        GPIO.output(STEP, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        time.sleep(delay)

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    # Disable the motor and clean up GPIO pins
    GPIO.output(ENABLE, GPIO.HIGH)
    GPIO.cleanup()
    print("GPIO cleaned up")

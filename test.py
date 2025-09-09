from gpiozero import OutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN = 13
DIR_PIN = 6
ENA_PIN = 12

# Initialize the pins as output devices
pul = PWMOutputDevice(PUL_PIN, active_high=True, frequency=100)
dir = OutputDevice(DIR_PIN, active_high=True)
ena = OutputDevice(ENA_PIN, active_high=False)

# Enable the driver
ena.on()
sleep(1)

# Test the movement with CW (Clockwise)
print("Starting CW rotation...")
dir.off()
pul.pulse(n=200, background=False)

sleep(1)

# Test the movement with CCW (Counter-Clockwise)
print("Starting CCW rotation...")
dir.on()
pul.pulse(n=200, background=False)

# End of test
print("Test complete.")

# Cleanup
pul.close()
dir.close()
ena.close()

from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN = 13    # Pulse pin
DIR_PIN = 6     # Direction pin
ENA_PIN = 5     # Enable pin

duty_cycle = 0.5  # 50% duty cycle for PWM
motor_speed = 100 # Speed of motor in frequency (Hz)

# Initialize the pins as output devices
pul = PWMOutputDevice(PUL_PIN, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dir = DigitalOutputDevice(DIR_PIN, active_high=True, pin_factory= None)  # Active high to rotate CW
ena = OutputDevice(ENA_PIN, active_high=False)  # Active low to enable the driver

# Enable the driver (this must be done to activate the TB6600)
ena.on()
sleep(1)  # Small delay to allow the driver to initialize

# Direction values (1 for CCW, 0 for CW)
# Test the movement with CW (Clockwise)
print("Starting CW rotation...")
dir.off() # Set direction to CW
pul.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 10, background=False) # Start PWM signal

sleep(1)  # Pause for a moment

# Test the movement with CCW (Counter-Clockwise)
print("Starting CCW rotation...")
dir.on() # Set direction to CCW
pul.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 10, background=False) # Start PWM signal

print("Test complete.")

# Cleanup
pul.close()
dir.close()
ena.close()
from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

duty_cycle = 0.75  # 50% duty cycle for PWM
motor_speed = 100 # Speed of motor in frequency (Hz)

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# Direction values (1 for CCW, 0 for CW)
# Test the movement with CW (Clockwise)
print("Starting X-axis CW rotation...")
dirX.off() # Set direction to CW
pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal

sleep(1)  # Pause for a moment

print("Starting Y-axis CW rotation...")
dirY.off() # Set direction to CW
pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal

sleep(1)  # Pause for a moment

# Test the movement with CCW (Counter-Clockwise)
print("Starting X-axis CCW rotation...")
dirX.on() # Set direction to CCW
pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal

sleep(1)  # Pause for a moment

print("Starting Y-axis CCW rotation...")
dirY.on() # Set direction to CCW
pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal

# End of test
print("Test complete.")

# Cleanup
pulX.close()
dirX.close()
pulY.close()
dirY.close()

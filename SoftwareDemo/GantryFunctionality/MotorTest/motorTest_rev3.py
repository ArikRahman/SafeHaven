from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

duty_cycle = 0.75  # 50% duty cycle for PWM
motor_speed = 1000 #speed of motor in frequency (Hz)

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# print("Test starting in 3 seconds...")

print("Starting Y-axis CW rotation (up)...")
dirY.on() # Set direction to CW
pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# print("Starting Y-axis CCW rotation (down)...")
# dirY.off() # Set direction to CCW
# pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# print("Starting X-axis CW rotation (right)...")
# dirX.on() # Set direction to CW
# pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# print("Starting X-axis CCW rotation (left)...")
# dirX.off() # Set direction to CCW
# pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# Cleanup
pulX.close()
dirX.close()
pulY.close()
dirY.close()

# End of test
print("Test complete.")
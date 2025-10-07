from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

duty_cycle = 0.50  # 50% duty cycle for PWM
motor_speed = 100 # Speed of motor in frequency (Hz)

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# Function Definitions
def motorMove(change_x, change_y):
    if change_x > 0:
        dirX.off() # Set direction to CW
        pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal
    elif change_x < 0:
        dirX.on() # Set direction to CCW
        pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal

    if change_y > 0:
        dirY.off() # Set direction to CW
        pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal
    elif change_y < 0:
        dirY.on() # Set direction to CCW
        pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 3, background=False) # Start PWM signal

# Main

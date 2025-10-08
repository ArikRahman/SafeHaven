from gpiozero import DigitalOutputDevice, PWMOutputDevice
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

# Path Gen Array Output Example: [(0, 10000), (0, 9708), (2250, 9708), (2250, 125), (3000, 125), (3000, 9708), (3750, 9708), (3750, 125), (4500, 125), (4500, 9708), (5250, 9708), (5250, 125), (6000, 125), (6000, 9708), (6750, 9708), (6750, 125), (7000, 125), (7000, 9708), (7000, 10000), (0, 10000)]

# Function Definitions
def motorMove(change_x, change_y, step_size='1/8', fade_in_time=0.5, fade_out_time=0.5, background=False):
    step_sizes = {
        '1': 1,
        '1/2': 2,
        '1/4': 4,
        '1/8': 8,
        '1/16': 16,
        '1/32': 32,
        '1/64': 64,
        '1/128': 128
    }

    total_unit_steps_x = 5 # max steps on x-axis using step size of 1
    total_unit_steps_y = 6 # max steps on y-axis using step size of 1
    steps_x = change_x * total_unit_steps_x * step_sizes[step_size] / 10000 # (Δx / x maximum)->(percentage of 10,000) * unit step maximum * microsteps
    steps_y = change_y * total_unit_steps_y * step_sizes[step_size] / 10000 # (Δy / y maximum)->(percentage of 10,000) * unit step maximum * microsteps

    if change_x > 0:
        dirX.off() # Set direction to CW
        pulX.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_x, background=background) # Start PWM signal
    elif change_x < 0:
        dirX.on() # Set direction to CCW
        pulX.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_x, background=background) # Start PWM signal

    if change_y > 0:
        dirY.off() # Set direction to CW
        pulY.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_y, background=background) # Start PWM signal
    elif change_y < 0:
        dirY.on() # Set direction to CCW
        pulY.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_y, background=background) # Start PWM signal
    
    return 1
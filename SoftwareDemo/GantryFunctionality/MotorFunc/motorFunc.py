from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep

def motorInit(PUL_PIN_X = 13, DIR_PIN_X = 6, PUL_PIN_Y = 12, DIR_PIN_Y = 16, duty_cycle=0.5, motor_speed=100):
    """
    Initializes the motor control pins.

    Parameters:
        PUL_PIN_X - GPIO pin for X-axis pulse control
        DIR_PIN_X - GPIO pin for X-axis direction control
        PUL_PIN_Y - GPIO pin for Y-axis pulse control
        DIR_PIN_Y - GPIO pin for Y-axis direction control
        duty_cycle - Initial % duty cycle for PWM (0 to 1)
        motor_speed - Frequency for PWM signal in Hz

    Returns:
        None
    """
    # Define global GPIO pin calls
    global pulX, dirX, pulY, dirY

    # Initialize the pins as output devices
    pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
    dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
    pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=duty_cycle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
    dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# PathGen Array Output Example: [(0, 10000), (0, 9708), (2250, 9708), (2250, 125), (3000, 125), (3000, 9708), (3750, 9708), (3750, 125), (4500, 125), (4500, 9708), (5250, 9708), (5250, 125), (6000, 125), (6000, 9708), (6750, 9708), (6750, 125), (7000, 125), (7000, 9708), (7000, 10000), (0, 10000)]

# Function Definitions
def motorMove(path_array=[[0,0],[0,0]], step_size='1/8', x_max=10000, y_max=10000, fade_in_time=0.5, fade_out_time=0.5, background=False):
    """
    Converts PathGen output array to motor movements.
    
    Parameters:
        path_arry - List of (x, y) coordinates to move through
        step_size - Microstep setting as a string (e.g., '1', '1/2', '1/4', '1/8', '1/16', '1/32', '1/64', '1/128')
        max_x - Maximum x-coordinate value for scaling
        max_y - Maximum y-coordinate value for scaling
        fade_in_time - Time to ramp up the motor speed
        fade_out_time - Time to ramp down the motor speed
        background - If True, run motor movement in the background and proceed to next line of code without waiting
    
    Returns:
        -1 if array is than or equal to 2 rows
        1 on success
    """
    
    if len(path_array) <= 2:
        print("Error: Path array must contain more than two points.")
        return -1
    
    step_dict = {
        '1': 1,
        '1/2': 2,
        '1/4': 4,
        '1/8': 8,
        '1/16': 16,
        '1/32': 32,
        '1/64': 64,
        '1/128': 128
    }

    gantry_unit_steps_x = 5 # max steps on x-axis of Gantry using step size of 1
    gantry_unit_steps_y = 6 # max steps on y-axis of Gantry using step size of 1
    
    for path_array_index in range(1, len(path_array)):
        # PathGen: delta of previous point to current point
        change_x = path_array[path_array_index][0] - path_array[path_array_index - 1][0] # Δx
        change_y = path_array[path_array_index][1] - path_array[path_array_index - 1][1] # Δy

        # Convert delta to number of steps
        steps_x = int((change_x / x_max) * gantry_unit_steps_x * step_dict[step_size]) # (Δx / x maximum)->(percentage of 10,000) * unit step maximum * microsteps
        steps_y = int((change_y / y_max) * gantry_unit_steps_y * step_dict[step_size]) # (Δy / y maximum)->(percentage of 10,000) * unit step maximum * microsteps

        # Execute motor movement
        # X-axis movement
        if change_x > 0:
            dirX.off() # Set direction to CW
            pulX.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_x, background=background) # Start PWM signal
        elif change_x < 0:
            dirX.on() # Set direction to CCW
            pulX.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_x, background=background) # Start PWM signal

        # Y-axis movement
        if change_y > 0:
            dirY.off() # Set direction to CW
            pulY.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_y, background=background) # Start PWM signal
        elif change_y < 0:
            dirY.on() # Set direction to CCW
            pulY.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n= steps_y, background=background) # Start PWM signal
    
    return 1
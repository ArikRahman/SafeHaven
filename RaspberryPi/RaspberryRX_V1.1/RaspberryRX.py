import RPi.GPIO as GPIO
import time
import serial # Serial communication

# Define GPIO pins for stepper motor
DIR_X = 8
STEP_X = 7
DIR_Y = 6
STEP_Y = 5
STEP_P = 9 # Radar trigger

# Define movement 
RIGHT = GPIO.HIGH
LEFT = GPIO.LOW
UP = GPIO.LOW
DOWN = GPIO.HIGH

# Motor speed settings
motor_speed = 0.0001 # 100 microseconds

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup([DIR_X, STEP_X, DIR_Y, STEP_Y, STEP_P], GPIO.OUT)

# Function to move the stepper motor
def step_motor(direction, step_pin, dir_pin, steps):
    GPIO.output(dir_pin, direction)
    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(motor_speed)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(motor_speed)

# Function to execute movements based on received coordinates
def move_to_coordinates(x, y, x_stepsize = 62, y_stepsize = 250):
    global last_x, last_y

    # Convert X, Y to motor steps
    x_steps = int(abs(x-last_x) / x_stepsize)
    y_steps = int(abs(y-last_y) / y_stepsize)

    # Determine movement direction
    x_dir = RIGHT if x > last_x else LEFT
    y_dir = UP if y > last_y else DOWN
    
    # Move x-axis
    step_motor(x_dir, STEP_X, DIR_X, x_steps)

    # Move y-axis
    step_motor(y_dir, STEP_Y, DIR_Y, y_steps)

    # Update last position
    last_x, last_y = x, y

# Initialize last position
last_x, last_y = 0, 0

# UART config
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout = 1)

# Main loop to receive and execute movements
while True:
    line = ser.readline().decode().strip()
    if line:
        x, y = map(float, line.split(','))
        print(f"Received coordinates: X = {x}, Y = {y}")
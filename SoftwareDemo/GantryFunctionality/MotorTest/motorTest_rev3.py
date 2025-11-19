from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

duty_cycle = 0.50  # 50% duty cycle for PWM
motor_speed = 3000 #speed of motor in frequency (Hz)

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=0, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=0, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

################# New code #################
def up(duration):
    print("Starting Y-axis CW rotation (up)...")
    dirY.on() # Set direction to CW
    pulY.value = duty_cycle
    sleep(duration) # Seconds
    pulY.value = 0

def down(duration):
    print("Starting Y-axis CCW rotation (down)...")
    dirY.off() # Set direction to CCW
    pulY.value = duty_cycle
    sleep(duration) # Seconds
    pulY.value = 0

def right(duration):
    print("Starting X-axis CW rotation (right)...")
    dirX.on() # Set direction to CW
    pulX.value = duty_cycle
    sleep(duration) # Seconds
    pulX.value = 0

def left(duration):
    print("Starting X-axis CCW rotation (left)...")
    dirX.off() # Set direction to CCW
    pulX.value = duty_cycle
    sleep(duration) # Seconds
    pulX.value = 0

def diagonal(X, Y): # Coordinates in seconds
    print(f"Performing ({X},{Y}) triangle...")

    # Determine how long to run each motor for
    xTime = abs(X)
    yTime = abs(Y)

    # Do nothing if 0,0
    if xTime == 0 and yTime == 0:
        return

    # Set directions
    if X > 0:
        dirX.on() # CW - right
    else:
        dirX.off() # CCW - left

    if Y > 0:
        dirY.on() # CW - up
    else:
        dirY.off() # CCW - down

    # Initialize to let both motors move
    if X != 0:
        pulX.value = duty_cycle
    if Y != 0:
        pulY.value = duty_cycle
    
    # Overlap to let longer axis run and stop shorter axis motor
    overlap = min(xTime, yTime)
    sleep(overlap)

    # Stop shorter axis
    if xTime > yTime:
        pulY.value = 0
        sleep(xTime - overlap)
    elif yTime > xTime:
        pulX.value = 0
        sleep(yTime - overlap)

    # Stop PWN
    pulX.value = 0
    pulY.value = 0

# Cleanup
def close():
    pulX.close()
    dirX.close()
    pulY.close()
    dirY.close()

# Function to demo to Hudson/Karim
def demo():
    print("Test starting in 3 seconds...")
    sleep(3)

    up(3)
    down(3)
    left(3)
    right(3)

    sleep(1)

    diagonal(3,5)
    # FIXME: try diagonal(0,5)
    sleep(1)

    diagonal(-3,-5)

    close()

    # End of test
    print("Test complete.")

######### Main #########
def main():
    demo()

if __name__ == "__main__":
    main()

################# Old code #################
# print("Starting Y-axis CW rotation (up)...")
# dirY.on() # Set direction to CW
# pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# print("Starting Y-axis CCW rotation (down)...")
# dirY.off() # Set direction to CCW
# pulY.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# print("Starting X-axis CW rotation (right)...")
# dirX.on() # Set direction to CW
# pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal

# print("Starting X-axis CCW rotation (left)...")
# dirX.off() # Set direction to CCW
# pulX.pulse(fade_in_time=0.5, fade_out_time=0.5, n= 5, background=False) # Start PWM signal
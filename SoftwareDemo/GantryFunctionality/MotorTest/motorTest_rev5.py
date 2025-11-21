# Revision 5 by Vincent
    # Executes path list

from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep, time

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

# Parameters
duty_cycle = 0.50  # 50% duty cycle for PWM
motor_speed = 3000 #speed of motor in frequency (Hz)
xUnit = 14.0 / 10000.0
yUnit = 33.0 / 10000.0

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=0, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=0, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# Vector List
vectorList = [
    (0, 10000), (0, 9708), (2250, 9708), (2250, 125), (3000, 125),
    (3000, 9708), (3750, 9708), (3750, 125), (4500, 125), (4500, 9708),
    (5250, 9708), (5250, 125), (6000, 125), (6000, 9708), (6750, 9708),
    (6750, 125), (7000, 125), (7000, 9708), (7000, 10000), (0, 10000)
]

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

def followSnakepath(coords):
    if not coords or len(coords) < 2:
        print("Path list must have at least two points")
        return
    
    # Start time
    start = time()

    print("Following snake path...")

    currentX, currentY = coords[0]

    for nextX, nextY in coords[1:]:
        dx = nextX - currentX
        dy = nextY - currentY

        # Horizontal
        if dx != 0:
            durationX = abs(dx) * xUnit
            if dx > 0:
                right(durationX)
                sleep(0.25)
            else:
                left(durationX)
                sleep(0.25)

        # Vertical
        if dy != 0:
            durationY = abs(dy) * yUnit
            if dy > 0:
                up(durationY)
                sleep(0.25)
            else:
                down(durationY)
                sleep(0.25)

        currentX, currentY = nextX, nextY

    # End time
    end = time()

    procedurelength = end - start

    print(f"Time elaped: {procedurelength:.2f}s")

# Cleanup
def close():
    pulX.close()
    dirX.close()
    pulY.close()
    dirY.close()

######### Main #########
def main():
    print("Test starting in 3 seconds...")
    sleep(3)

    # up(33)

    # right(14)
    # sleep(1)
    # left(14)

    # down(33)
    # sleep(1)
    # up(33)

    followSnakepath(vectorList)

    close()

    # End of test
    print("Test complete.")

if __name__ == "__main__":
    main()
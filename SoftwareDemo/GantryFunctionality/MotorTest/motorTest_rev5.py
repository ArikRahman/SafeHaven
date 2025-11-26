# Revision 5 by Vincent
    # Executes path list
    # Smooth motor travel
    # Reed switch detection

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep, time

# Define the GPIO pins
PUL_PIN_X = 13 # Pulse pin x-axis
DIR_PIN_X = 6  # Direction pins x-axis
PUL_PIN_Y = 12 # Pulse pin y-axis
DIR_PIN_Y = 16 # Direction pins y-axis

# Parameters
duty_cycle = 0.50   # 50% duty cycle for PWM
f_x = 6400          # PWM frequency for X-axis in Hz
f_y = 6400          # PWM frequency for Y-axis in Hz

steps_per_rev = 1600  # Microsteps per revolution for the motor, dictated by driver settings
length_per_rev = 10   # Length per revolution in mm
total_distance = 675  # Total traveling distance in mm for both axes
total_pixels = 10000  # Total pixels for both axes

# X-axis speed calculations
speedX_rev_per_s = f_x / steps_per_rev  # Speed in revolutions per second
speedX_mm_per_s = (speedX_rev_per_s) * length_per_rev  # Speed in mm/s
speedX_pixels_per_s = (speedX_mm_per_s / total_distance) * total_pixels  # Speed in pixels/s

# Y-axis speed calculations
speedY_rev_per_s = f_y / steps_per_rev  # Speed in revolutions per second
speedY_mm_per_s = (speedY_rev_per_s) * length_per_rev  # Speed in mm/s
speedY_pixels_per_s = (speedY_mm_per_s / total_distance) * total_pixels  # Speed in pixels/s

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=0, frequency=f_x, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=0, frequency=f_y, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# Vector List
vectorListContinuous = [(0, 10000), (0, 9915), (2094, 9915), (2094, 85), (2844, 85), (2844, 9915), (3594, 9915), (3594, 85), (4344, 85), (4344, 9915), (5094, 9915), (5094, 85), (5844, 85), (5844, 9915), (6594, 9915), (6594, 85), (7156, 85), (7156, 9915), (7156, 10000), (0, 10000)]
vectorListDiscrete = [(0, 10000), (0, 9915), (2094, 9915), (2094, 7949), (2094, 5983), (2094, 4017), (2094, 2051), (2094, 85), (2844, 85), (2844, 2051), (2844, 4017), (2844, 5983), (2844, 7949), (2844, 9915), (3594, 9915), (3594, 7949), (3594, 5983), (3594, 4017), (3594, 2051), (3594, 85), (4344, 85), (4344, 2051), (4344, 4017), (4344, 5983), (4344, 7949), (4344, 9915), (5094, 9915), (5094, 7949), (5094, 5983), (5094, 4017), (5094, 2051), (5094, 85), (5844, 85), (5844, 2051), (5844, 4017), (5844, 5983), (5844, 7949), (5844, 9915), (6594, 9915), (6594, 7949), (6594, 5983), (6594, 4017), (6594, 2051), (6594, 85), (7156, 85), (7156, 2051), (7156, 4017), (7156, 5983), (7156, 7949), (7156, 9915), (7156, 10000), (0, 10000)]

# Pixels (10000 x 10000)
def up(pixels):
    print("Starting Y-axis CW rotation (up)...")
    dirY.on() # Set direction to CW
    pulY.value = duty_cycle
    sleep(abs(pixels)/speedY_pixels_per_s) # Seconds
    pulY.value = 0

def down(pixels):
    print("Starting Y-axis CCW rotation (down)...")
    dirY.off() # Set direction to CCW
    pulY.value = duty_cycle
    sleep(abs(pixels)/speedY_pixels_per_s) # Seconds
    pulY.value = 0

def right(pixels):
    print("Starting X-axis CW rotation (right)...")
    dirX.on() # Set direction to CW
    pulX.value = duty_cycle
    sleep(abs(pixels)/speedX_pixels_per_s) # Seconds
    pulX.value = 0

def left(pixels):
    print("Starting X-axis CCW rotation (left)...")
    dirX.off() # Set direction to CCW
    pulX.value = duty_cycle
    sleep(abs(pixels)/speedX_pixels_per_s) # Seconds
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
    stopAll()

def stopX():
    pulX.value = 0

def stopY():
    pulY.value = 0

def stopAll():
    stopX()
    stopY()

def followSnakepath(coords):
    if not coords or len(coords) < 2:
        print("Path list must have at least two points")
        return
    
    # Start time
    start = time()

    print("Following snake path...")

    currentX, currentY = coords[0]

    # Iterate through rest of path list cords
    for nextX, nextY in coords[1:]:
        dx = nextX - currentX
        dy = nextY - currentY

        # Horizontal
        if dx != 0:
            if dx > 0:
                right(dx)
                sleep(0.25)
            else:
                left(dx)
                sleep(0.25)

        # Vertical
        if dy != 0:
            if dy > 0:
                up(dy)
                sleep(0.25)
            else:
                down(dy)
                sleep(0.25)

        currentX, currentY = nextX, nextY

    # End time
    end = time()

    procedurelength = end - start

    print(f"Time elaped: {procedurelength:.2f}s, ({procedurelength//60:.0f} minute : {procedurelength%60:.0f} second)")

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

    up(9000)
    # down(3000)

    # followSnakepath(vectorListDiscrete)

    close()

    # End of test
    print("Test complete.")

if __name__ == "__main__":
    main()
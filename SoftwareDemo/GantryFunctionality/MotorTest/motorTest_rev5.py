# Revision 5 by Vincent
    # Executes path list
    # Smooth motor travel

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep, time

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis


# Parameters
duty_cycle = 0.50  # 50% duty cycle for PWM
f_x = 64000 # PWM frequency for X-axis in Hz
f_y = 32000 # PWM frequency for Y-axis in Hz

steps_per_rev = 32000  # Microsteps per revolution for the motor, dictated by driver settings
length_per_rev = 5  # Length per revolution in mm
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

motor_speed = 3000 #speed of motor in frequency (Hz)
xUnit = 14.0 / 10000.0
yUnit = 17.0 / 10000.0

MotorPresets = {
    "3000": {"xUnit": 14.0 / 10000.0, "yUnit": 33.0 / 10000.0},
}

# Initialize the pins as output devices
pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=0, frequency=f_x, pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=0, frequency=f_y, pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW

# Vector List
vectorList = [(0, 10000), (0, 9958), (2094, 9958), (2094, 83), (2844, 83), (2844, 9958), (3594, 9958), (3594, 83), (4344, 83), (4344, 9958), (5094, 9958), (5094, 83), (5844, 83), (5844, 9958), (6594, 9958), (6594, 83), (7156, 83), (7156, 9958), (7156, 10000), (0, 10000)]

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

    # down(17)
    # sleep(1)
    # up(17)

    # right(14)
    # sleep(1)
    # left(14)

    followSnakepath(vectorList)

    close()

    # End of test
    print("Test complete.")

if __name__ == "__main__":
    main()
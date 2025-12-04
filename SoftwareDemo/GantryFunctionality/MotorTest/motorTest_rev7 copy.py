# Revision 6 by Corban
    # Executes path list
    # Stepping motor travel

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep, time
from pynput import keyboard
import threading


# Define the GPIO pins
PUL_PIN_X = 13 # Pulse pin x-axis
DIR_PIN_X = 6  # Direction pins x-axis
PUL_PIN_Y = 12 # Pulse pin y-axis
DIR_PIN_Y = 16 # Direction pins y-axis


# Parameters
duty_cycle = 0.50  # 50% duty cycle for PWM
f_x = 6400 # PWM frequency for X-axis in Hz
f_y = 6400 # PWM frequency for Y-axis in Hz
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
pulX = PWMOutputDevice(PUL_PIN_X, 
                       active_high=True, 
                       initial_value=0, 
                       frequency=f_x, 
                       pin_factory= None)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, 
                           active_high=True, 
                           pin_factory= None)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, 
                       active_high=True, 
                       initial_value=0, 
                       frequency=f_y, 
                       pin_factory= None)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, 
                           active_high=True, 
                           pin_factory= None)  # Active high to rotate CW


# Vector List
vectorListContinuous = [(0, 10000), (0, 9915), 
                        (2094, 9915), (2094, 85), 
                        (2844, 85), (2844, 9915), 
                        (3594, 9915), (3594, 85), 
                        (4344, 85), (4344, 9915), 
                        (5094, 9915), (5094, 85), 
                        (5844, 85), (5844, 9915), 
                        (6594, 9915), (6594, 85), 
                        (7156, 85), (7156, 9915), 
                        (7156, 10000), (0, 10000)]
vectorListDiscrete = [(0, 10000), (0, 9900), 
                      (2094, 9900), (2094, 7940), (2094, 5980), (2094, 4020), (2094, 2060), (2094, 100), 
                      (2844, 100), (2844, 2060), (2844, 4020), (2844, 5980), (2844, 7940), (2844, 9900), 
                      (3594, 9900), (3594, 7940), (3594, 5980), (3594, 4020), (3594, 2060), (3594, 100), 
                      (4344, 100), (4344, 2060), (4344, 4020), (4344, 5980), (4344, 7940), (4344, 9900), 
                      (5094, 9900), (5094, 7940), (5094, 5980), (5094, 4020), (5094, 2060), (5094, 100), 
                      (5844, 100), (5844, 2060), (5844, 4020), (5844, 5980), (5844, 7940), (5844, 9900), 
                      (6594, 9900), (6594, 7940), (6594, 5980), (6594, 4020), (6594, 2060), (6594, 100), 
                      (7156, 100), (7156, 2060), (7156, 4020), (7156, 5980), (7156, 7940), (7156, 9900), 
                      (7156, 10000), (0, 10000)]
vectorListDiscrete_test = [(0, 10000), (0, 9900), 
                      (2094, 9900), (2094, 7940), (2094, 5980), (2094, 4020), (2094, 2060), (2094, 100), (2094, 9900),
                      (2844, 9900), (2844, 7940), (2844, 5980), (2844, 4020), (2844, 2060), (2844, 100), (2844, 9900), 
                      (3594, 9900), (3594, 7940), (3594, 5980), (3594, 4020), (3594, 2060), (3594, 100), (3594, 9900),
                      (4344, 9900), (4344, 7940), (4344, 5980), (4344, 4020), (4344, 2060), (4344, 100), (4344, 9900), 
                      (5094, 9900), (5094, 7940), (5094, 5980), (5094, 4020), (5094, 2060), (5094, 100), (5094, 9900),
                      (5844, 9900), (5844, 7940), (5844, 5980), (5844, 4020), (5844, 2060), (5844, 100), (5844, 9900), 
                      (6594, 9900), (6594, 7940), (6594, 5980), (6594, 4020), (6594, 2060), (6594, 100), (6594, 9900),
                      (7156, 9900), (7156, 7940), (7156, 5980), (7156, 4020), (7156, 2060), (7156, 100), (7156, 9900), 
                      (7156, 10000), (0, 10000)]


# Create a global event
right_arrow_pressed = threading.Event()


def on_press(key):
    # Special keys like arrows
    if key == keyboard.Key.left:
        print("Left arrow detected! Stopping motors.")
        stopAllMotor()

    # Keep any other handlers you need
    if key == keyboard.Key.right:
        print("Right arrow detected!")
        right_arrow_pressed.set()  # Signal to main loop

def on_release(key):
    if key == keyboard.Key.esc:
        print("Esc pressed — stopping listener.")
        return False  # Stop listener thread

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

def followSnakepath(coords, discrete=False):
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
                if discrete == True:
                    print("Waiting for right arrow...") # Waits here until right arrow is pressed
                    right_arrow_pressed.wait()
                    # print("Right arrow received!") # Clear event so next loop iteration waits again
                    right_arrow_pressed.clear()

                up(dy)          
                sleep(0.25)
            else:
                if discrete == True:
                    print("Waiting for right arrow...") # Waits here until right arrow is pressed
                    right_arrow_pressed.wait()
                    # print("Right arrow received!") # Clear event so next loop iteration waits again
                    right_arrow_pressed.clear()
                
                down(dy)
                sleep(0.25)

        currentX, currentY = nextX, nextY

    # End time
    end = time()

    stopAllMotor()

    procedurelength = end - start

    print(f"Time elaped: {procedurelength:.2f}s, ({procedurelength//60:.0f} minute : {procedurelength%60:.0f} second)")

def stopX_Motor():
    pulX.value = 0

def stopY_Motor():
    pulY.value = 0

def stopAllMotor():
    stopX_Motor()
    stopY_Motor()

# Cleanup
def close():
    pulX.close()
    dirX.close()
    pulY.close()
    dirY.close()

######### Main #########
def main():
    # Start listener in background
    if 1:
        listener = keyboard.Listener(
            on_press=on_press, 
            on_release=on_release, 
            suppress=False)
        listener.start()
    
    print(f"Setting x-axis speed: {speedX_pixels_per_s:.2f} pixels/s, {speedX_mm_per_s:.2f} mm/s or {speedX_mm_per_s / 25.4:.2f} in/s, {speedX_rev_per_s:.2f} rev/s")
    print(f"Setting y-axis speed: {speedY_pixels_per_s:.2f} pixels/s, {speedY_mm_per_s:.2f} mm/s or {speedY_mm_per_s / 25.4:.2f} in/s, {speedY_rev_per_s:.2f} rev/s")
    print("Test starting in 3 seconds...")
    sleep(3)

    if 0:
        # up(1000)
        # sleep(1)
        # down(1000)
        # right(8000)
        sleep(1)
        left(2000)
    
    if 1:
        followSnakepath(vectorListDiscrete, discrete=True)
        listener.stop()

    close()

    # End of test
    print("Test complete.")

if __name__ == "__main__":
    main()
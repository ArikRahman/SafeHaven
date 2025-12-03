# Revision 10 by Corban
    # Executes path list
    # Stepping motor travel

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep, time
import sys
import os


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


def up(pixels):
    dirY.on() # Set direction to CW
    pulY.value = duty_cycle
    sleep(abs(pixels)/speedY_pixels_per_s) # Seconds
    pulY.value = 0

def down(pixels):
    dirY.off() # Set direction to CCW
    pulY.value = duty_cycle
    sleep(abs(pixels)/speedY_pixels_per_s) # Seconds
    pulY.value = 0

def right(pixels):
    dirX.on() # Set direction to CW
    pulX.value = duty_cycle
    sleep(abs(pixels)/speedX_pixels_per_s) # Seconds
    pulX.value = 0

def left(pixels):
    dirX.off() # Set direction to CCW
    pulX.value = duty_cycle
    sleep(abs(pixels)/speedX_pixels_per_s) # Seconds
    pulX.value = 0

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
    if "next" in sys.argv:
        # Load current index
        if os.path.exists("current_index.txt"):
            with open("current_index.txt", "r") as f:
                current_index = int(f.read().strip())
        else:
            current_index = 0
        
        coords = vectorListDiscrete
        
        if current_index == 0:
            pass
        
        if current_index >= len(coords) - 1:
            close()
            return
        
        currentX, currentY = coords[current_index]
        
        # Find the next index where dy != 0
        next_index = current_index + 1
        while next_index < len(coords):
            nextX, nextY = coords[next_index]
            dx = nextX - currentX
            dy = nextY - currentY
            if dx != 0:
                if dx > 0:
                    right(dx)
                    sleep(0.25)
                else:
                    left(dx)
                    sleep(0.25)
            if dy != 0:
                if dy > 0:
                    up(dy)
                    sleep(0.25)
                else:
                    down(dy)
                    sleep(0.25)
                break
            currentX, currentY = nextX, nextY
            next_index += 1
        
        stopAllMotor()
        
        # Save new index
        with open("current_index.txt", "w") as f:
            f.write(str(next_index))
        
        if next_index >= len(coords) - 1:
            close()
            os.remove("current_index.txt")

if __name__ == "__main__":
    main()
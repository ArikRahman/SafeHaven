# Revision 10 by Corban
    # Executes path list
    # Stepping motor travel

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep
import sys
import os
import json


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
MARGIN_PIXELS = 200  # How far from the borders we want motions to stay (in pixels)

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
                       frequency=f_x)  # PWM for pulse control
dirX = DigitalOutputDevice(DIR_PIN_X, 
                           active_high=True)  # Active high to rotate CW
pulY = PWMOutputDevice(PUL_PIN_Y, 
                       active_high=True, 
                       initial_value=0, 
                       frequency=f_y)  # PWM for pulse control
dirY = DigitalOutputDevice(DIR_PIN_Y, 
                           active_high=True)  # Active high to rotate CW


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


def apply_margin(coords, margin=MARGIN_PIXELS, max_pixels=total_pixels):
    """Clamp each coordinate pair inside the range [margin, max_pixels - margin].

    This keeps the gantry from traveling to the extreme border or outside it.
    """
    if margin <= 0:
        return coords
    inset = []
    for x, y in coords:
        # Ensure integer arithmetic; preserve integers from original coordinates
        cx = int(min(max(x, margin), max_pixels - margin))
        cy = int(min(max(y, margin), max_pixels - margin))
        inset.append((cx, cy))
    return inset


# Create inset (margined) variants of the travel vectors
vectorListContinuous_inset = apply_margin(vectorListContinuous, MARGIN_PIXELS)
vectorListDiscrete_inset = apply_margin(vectorListDiscrete, MARGIN_PIXELS)
vectorListDiscrete_test_inset = apply_margin(vectorListDiscrete_test, MARGIN_PIXELS)


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


def save_position(currentX, currentY, coords=None, filename='position.txt'):
    """Save current position and optionally all coords to a file as JSON.

    Format: {"current_pos": [x, y], "coords": [[x1, y1], ...], "current_index": int}
    """
    data = {
        'current_pos': [int(currentX), int(currentY)]
    }
    if coords is not None:
        data['coords'] = coords
    # attempt to also save the index for convenience if we can find it
    try:
        idx = None
        if coords is not None:
            for i, (x, y) in enumerate(coords):
                if x == int(currentX) and y == int(currentY):
                    idx = i
                    break
        if idx is not None:
            data['current_index'] = idx
    except Exception:
        pass

    with open(filename, 'w') as f:
        json.dump(data, f)


def load_position(filename='position.txt'):
    """Load position info from `position.txt` if present. Returns dict or None"""
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            return data
    except Exception:
        return None


def move_both(dx, dy, duty=duty_cycle):
    """Move both motors simultaneously according to dx, dy in pixels.

    This sets directions, starts PWM for both motors, and stops each when
    its travel time is completed.
    """
    # set directions
    if dx > 0:
        dirX.on()
    elif dx < 0:
        dirX.off()
    if dy > 0:
        dirY.on()
    elif dy < 0:
        dirY.off()

    # compute duration; zero distances should have zero time
    timeX = abs(dx) / speedX_pixels_per_s if dx != 0 else 0
    timeY = abs(dy) / speedY_pixels_per_s if dy != 0 else 0

    # start both
    if dx != 0:
        pulX.value = duty
    if dy != 0:
        pulY.value = duty

    # if both times are >0 then coordinate stopping times
    if timeX > 0 and timeY > 0:
        # sleep until the shorter one finishes
        if timeX == timeY:
            sleep(timeX)
            pulX.value = 0
            pulY.value = 0
            return
        if timeX > timeY:
            sleep(timeY)
            # stop Y
            pulY.value = 0
            # finish X
            sleep(timeX - timeY)
            pulX.value = 0
            return
        else:
            # timeY > timeX
            sleep(timeX)
            pulX.value = 0
            sleep(timeY - timeX)
            pulY.value = 0
            return

    # If we only need to move X or Y
    if timeX > 0 and timeY == 0:
        sleep(timeX)
        pulX.value = 0
    elif timeY > 0 and timeX == 0:
        sleep(timeY)
        pulY.value = 0

######### Main #########
def main():
    if "next" in sys.argv:
        # Load current index
        if os.path.exists("current_index.txt"):
            with open("current_index.txt", "r") as f:
                current_index = int(f.read().strip())
        else:
            current_index = 0
        
        # Allow a custom margin to be passed as a command-line argument as
        # `margin=<pixels>` or `--margin=<pixels>`. If not, use the default MARGIN_PIXELS.
        chosen_margin = MARGIN_PIXELS
        for arg in sys.argv:
            if arg.startswith('--margin=') or arg.startswith('margin='):
                try:
                    chosen_margin = int(arg.split('=')[1])
                except ValueError:
                    pass

        # Compute coords for the chosen margin so the gantry stays away from borders
        coords = apply_margin(vectorListDiscrete, chosen_margin)
        
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
            # If a vertical movement exists, treat it as the break point for this run
            if dy != 0:
                if dx != 0:
                    move_both(dx, dy)
                else:
                    # only Y change
                    if dy > 0:
                        up(dy)
                    else:
                        down(dy)
                # arrived at next index coordinate
                break
            # No vertical movement, keep moving horizontally and advance index
            if dx != 0:
                if dx > 0:
                    right(dx)
                else:
                    left(dx)
            currentX, currentY = nextX, nextY
            next_index += 1
        
        stopAllMotor()

        # Set the current position to the arrived-to coordinate, save index and position
        try:
            currentX, currentY = coords[next_index]
        except Exception:
            # if next_index is out of range, keep current
            pass

        # Save new index and position
        with open("current_index.txt", "w") as f:
            f.write(str(next_index))
        save_position(currentX, currentY, coords)
        
        if next_index >= len(coords) - 1:
            close()
            os.remove("current_index.txt")

    if "origin" in sys.argv:
        # Bring gantry to the origin (approximate to the in-margin origin)
        chosen_margin = MARGIN_PIXELS
        for arg in sys.argv:
            if arg.startswith('--margin=') or arg.startswith('margin='):
                try:
                    chosen_margin = int(arg.split('=')[1])
                except ValueError:
                    pass

        coords_inset = apply_margin(vectorListDiscrete, chosen_margin)

        originX, originY = coords_inset[0]  # use the first coordinate in list as origin

        # Determine current position from position.txt if available, or from current_index
        pos_info = load_position()
        if pos_info and 'current_pos' in pos_info:
            currentX, currentY = pos_info['current_pos']
        else:
            if os.path.exists('current_index.txt'):
                with open('current_index.txt', 'r') as f:
                    try:
                        current_index = int(f.read().strip())
                    except Exception:
                        current_index = 0
            else:
                current_index = 0
            currentX, currentY = coords_inset[current_index]

        dx = originX - currentX
        dy = originY - currentY

        # Move both motors at once to origin
        if dx != 0 and dy != 0:
            move_both(dx, dy)
        elif dx != 0:
            if dx > 0:
                right(dx)
            else:
                left(dx)
        elif dy != 0:
            if dy > 0:
                up(dy)
            else:
                down(dy)

        # stop and save new position (origin); update index to 0
        stopAllMotor()
        with open('current_index.txt', 'w') as f:
            f.write('0')
        save_position(originX, originY, coords_inset)

if __name__ == "__main__":
    main()
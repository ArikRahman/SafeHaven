# Revision 10 by Corban
# Executes path list
# Stepping motor travel
#
# Quick CLI usage:
#   python3 motorTest_rev10.py next
#   python3 motorTest_rev10.py origin --margin=200
#   python3 motorTest_rev10.py up                       # default step
#   python3 motorTest_rev10.py up=50                    # step=50
#   python3 motorTest_rev10.py go right 100            # shorthand
#   python3 motorTest_rev10.py go 100 right            # shorthand
#   python3 motorTest_rev10.py go=100 right            # shorthand
#   python3 motorTest_rev10.py --step=50 up            # override global step
#   python3 motorTest_rev10.py left=200 --force        # 'force' allows ignore margin clamp and prevents saving position

from gpiozero import DigitalOutputDevice, PWMOutputDevice
from time import sleep, time
import sys
import os
import json
import tty
import termios
import select


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
STEP_PIXELS = 200  # Default 'small' step used for direction-only commands

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


def clamp_to_margin(value, margin=MARGIN_PIXELS, max_pixels=total_pixels):
    return int(min(max(value, margin), max_pixels - margin))


def clamp_to_bounds(value, max_pixels=total_pixels):
    """Clamp to absolute bounds [0, max_pixels]."""
    return int(min(max(value, 0), max_pixels))


def find_index_for_pos(coords, x, y):
    for i, (cx, cy) in enumerate(coords):
        if int(cx) == int(x) and int(cy) == int(y):
            return i
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


def read_key(timeout=0.1):
    """Read a single key press in a non-blocking manner and return the string value.

    Returns None if no key pressed in timeout.
    Handles arrow keys (escape sequences) and single-letter keys.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([fd], [], [], timeout)
        if r:
            ch = os.read(fd, 3)
            try:
                return ch.decode()
            except Exception:
                return None
        else:
            return None
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def arcade_mode(initialX, initialY, step=STEP_PIXELS, chosen_margin=MARGIN_PIXELS, force_flag=False):
    """Interactive keyboard mode for arcade-style manual control.

    Use arrow keys or WASD for movement; 'q' to quit; 'f' to toggle force; 'p' to print current position.
    Each key press moves by `step` pixels; use --step to customize when calling the script.
    """
    print('\nEntering arcade mode. Arrow keys / WASD to move; q to quit; f to toggle force; p to print position; s to save')
    currentX = int(initialX)
    currentY = int(initialY)
    coords_inset = apply_margin(vectorListDiscrete, chosen_margin)
    print(f'Initial pos: {currentX}, {currentY}; step: {step}; margin: {chosen_margin}; force: {force_flag}')
    try:
        while True:
            k = read_key(0.1)
            if k is None:
                continue
            # Map arrow keys and WASD
            key = None
            if k in ('w', 'W', 'k') or k == '\x1b[A' or k == '\x1b[OA':
                key = 'up'
            elif k in ('s', 'S', 'j') or k == '\x1b[B' or k == '\x1b[OB':
                key = 'down'
            elif k in ('a', 'A', 'h') or k == '\x1b[D' or k == '\x1b[OD':
                key = 'left'
            elif k in ('d', 'D', 'l') or k == '\x1b[C' or k == '\x1b[OC':
                key = 'right'
            elif k in ('q', 'Q'):
                print('Exiting arcade mode.')
                break
            elif k in ('f', 'F'):
                force_flag = not force_flag
                print('toggle force ->', force_flag)
                continue
            elif k in ('p', 'P'):
                print('pos:', currentX, currentY)
                continue
            elif k in ('s', 'S'):
                save_position(currentX, currentY, coords_inset)
                print('Saved position')
                continue
            elif k in (' ',):  # space to stop
                stopAllMotor()
                continue
            else:
                # Not a recognized key
                continue

            # compute dx/dy
            dx = 0
            dy = 0
            if key == 'up':
                dy = int(step)
            elif key == 'down':
                dy = -int(step)
            elif key == 'right':
                dx = int(step)
            elif key == 'left':
                dx = -int(step)

            # Compute target; if force, allow bounds; otherwise clamp to margin
            if force_flag:
                targetX = clamp_to_bounds(currentX + dx)
                targetY = clamp_to_bounds(currentY + dy)
            else:
                targetX = currentX if dx == 0 else clamp_to_margin(currentX + dx, chosen_margin, total_pixels)
                targetY = currentY if dy == 0 else clamp_to_margin(currentY + dy, chosen_margin, total_pixels)

            new_dx = targetX - currentX
            new_dy = targetY - currentY
            if new_dx == 0 and new_dy == 0:
                # Nothing to move
                continue

            # Do movement
            if new_dx != 0 and new_dy != 0:
                move_both(new_dx, new_dy)
            elif new_dx != 0:
                if new_dx > 0:
                    right(new_dx)
                else:
                    left(abs(new_dx))
            elif new_dy != 0:
                if new_dy > 0:
                    up(new_dy)
                else:
                    down(abs(new_dy))

            # Update current position unless we are forced not to.
            if not force_flag:
                currentX = targetX
                currentY = targetY
                # Update index if matches.
                idx = find_index_for_pos(coords_inset, currentX, currentY)
                if idx is not None:
                    with open('current_index.txt', 'w') as f:
                        f.write(str(idx))
                save_position(currentX, currentY, coords_inset)
            print('moved ->', targetX, targetY, 'force:', force_flag)
    finally:
        stopAllMotor()
        print('Arcade mode stopped; motors halted.')

def start_motion(action):
    """Start motor movement in a specific direction (non-blocking)."""
    if action == 'up':
        dirY.on()
        pulY.value = duty_cycle
    elif action == 'down':
        dirY.off()
        pulY.value = duty_cycle
    elif action == 'right':
        dirX.on()
        pulX.value = duty_cycle
    elif action == 'left':
        dirX.off()
        pulX.value = duty_cycle

def arcade_mode_live(initialX, initialY, chosen_margin=MARGIN_PIXELS, force_flag=False):
    """
    Live arcade mode using terminal input (works over SSH/headless).
    Simulates 'hold-to-move' by using a watchdog timer on key repeats.
    """
    print('\nEntering LIVE arcade mode (terminal). Hold keys to move (WASD/Arrows). q to quit. p for pos.')
    
    currentX = float(initialX)
    currentY = float(initialY)
    
    current_action = None
    move_start_time = 0
    last_key_time = 0
    
    # Watchdog threshold: if no key for this long, stop motors.
    # Typical keyboard repeat rate is ~30Hz (33ms). 0.15s is a safe buffer.
    STOP_THRESHOLD = 0.15 

    try:
        while True:
            # Short timeout to allow checking the watchdog
            k = read_key(timeout=0.05)
            now = time()
            
            # Map key to action
            new_action = None
            if k is not None:
                if k in ('w', 'W', 'k') or k == '\x1b[A' or k == '\x1b[OA':
                    new_action = 'up'
                elif k in ('s', 'S', 'j') or k == '\x1b[B' or k == '\x1b[OB':
                    new_action = 'down'
                elif k in ('a', 'A', 'h') or k == '\x1b[D' or k == '\x1b[OD':
                    new_action = 'left'
                elif k in ('d', 'D', 'l') or k == '\x1b[C' or k == '\x1b[OC':
                    new_action = 'right'
                elif k in ('q', 'Q'):
                    break
                elif k in ('p', 'P'):
                    print(f'Pos: {int(currentX)}, {int(currentY)}')
                    continue
            
            # State Machine
            if new_action:
                last_key_time = now
                
                if new_action != current_action:
                    # Direction changed!
                    # 1. Stop previous
                    if current_action:
                        dt = now - move_start_time
                        # Update position for the segment just finished
                        if current_action in ('up', 'down'):
                            dist = dt * speedY_pixels_per_s * (1 if current_action == 'up' else -1)
                            currentY += dist
                        else:
                            dist = dt * speedX_pixels_per_s * (1 if current_action == 'right' else -1)
                            currentX += dist
                        stopAllMotor()
                        print(f"Pos: {int(currentX)}, {int(currentY)}")

                    # 2. Start new
                    current_action = new_action
                    move_start_time = now
                    start_motion(current_action)
            
            else:
                # No key pressed this cycle. Check watchdog.
                if current_action is not None:
                    if (now - last_key_time) > STOP_THRESHOLD:
                        # Timeout! Stop motors.
                        dt = last_key_time - move_start_time # Use last known key time for accuracy
                        # (Or use 'now' if you prefer to count the silence as movement, but usually safer to stop at last key)
                        # Let's use a mix: the motor WAS running until now, but maybe we should credit up to threshold?
                        # Simplest: credit up to 'now' minus a tiny bit, or just 'now'. 
                        # Since we poll fast, 'now' is fine.
                        dt = now - move_start_time
                        
                        if current_action in ('up', 'down'):
                            dist = dt * speedY_pixels_per_s * (1 if current_action == 'up' else -1)
                            currentY += dist
                        else:
                            dist = dt * speedX_pixels_per_s * (1 if current_action == 'right' else -1)
                            currentX += dist
                        
                        stopAllMotor()
                        current_action = None
                        print(f"Stopped. Pos: {int(currentX)}, {int(currentY)}")
                        
                        # Save position on stop
                        if not force_flag:
                            coords_inset = apply_margin(vectorListDiscrete, chosen_margin)
                            # Clamp to margin before saving
                            currentX = min(max(currentX, chosen_margin), total_pixels - chosen_margin)
                            currentY = min(max(currentY, chosen_margin), total_pixels - chosen_margin)
                            save_position(currentX, currentY, coords_inset)
                        else:
                            # Just clamp to bounds
                            currentX = min(max(currentX, 0), total_pixels)
                            currentY = min(max(currentY, 0), total_pixels)

            # Safety Clamp Check (while moving)
            if current_action:
                # Predict where we are roughly
                dt = now - move_start_time
                tempX, tempY = currentX, currentY
                if current_action == 'up': tempY += dt * speedY_pixels_per_s
                elif current_action == 'down': tempY -= dt * speedY_pixels_per_s
                elif current_action == 'right': tempX += dt * speedX_pixels_per_s
                elif current_action == 'left': tempX -= dt * speedX_pixels_per_s
                
                # Check bounds
                limit = total_pixels if force_flag else (total_pixels - chosen_margin)
                lower = 0 if force_flag else chosen_margin
                
                if tempX < lower or tempX > limit or tempY < lower or tempY > limit:
                    print("Hit limit!")
                    stopAllMotor()
                    # Update real pos
                    currentX, currentY = tempX, tempY
                    current_action = None

    finally:
        stopAllMotor()
        print('Arcade mode stopped.')


######### Main #########
def main():
    # Check for arcade mode first
    arcade_flag = False
    for arg in sys.argv:
        if arg.lstrip('-').startswith('arcade'):
            arcade_flag = True
            break
    
    if arcade_flag:
        # Load position
        pos_info = load_position()
        pos_info = load_position()
        if pos_info and 'current_pos' in pos_info:
            currentX, currentY = pos_info['current_pos']
        else:
            current_index = 0
            if os.path.exists('current_index.txt'):
                with open('current_index.txt', 'r') as f:
                    try:
                        current_index = int(f.read().strip())
                    except Exception:
                        current_index = 0
            coords_inset = apply_margin(vectorListDiscrete, MARGIN_PIXELS)
            currentX, currentY = coords_inset[current_index]

        chosen_margin = MARGIN_PIXELS
        for arg in sys.argv:
            if arg.startswith('--margin=') or arg.startswith('margin='):
                try:
                    chosen_margin = int(arg.split('=')[1])
                except ValueError:
                    pass
        
        force_flag = False
        for a in sys.argv:
            if a.lstrip('-').split('=', 1)[0] == 'force':
                force_flag = True

        arcade_mode_live(currentX, currentY, chosen_margin=chosen_margin, force_flag=force_flag)
        return

    # Priority order: next -> origin -> directional commands
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
        return

    # Directional micro-movements: up/down/left/right optionally with =<pixels>. Supports multiple at once
    # and the 'go' shorthand. Examples:
    # - python3 motorTest_rev10.py go right 100
    # - python3 motorTest_rev10.py go 100 right
    # - python3 motorTest_rev10.py go=100 right
    # - python3 motorTest_rev10.py go 100   -> defaults to 'right'
    # - python3 motorTest_rev10.py up right=100 --step=80
    dir_args = {}
    tokens = [arg.lstrip('-') for arg in sys.argv[1:]]
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        # inline form like right=100
        if '=' in tok:
            key, val = tok.split('=', 1)
            if key in ('up', 'down', 'left', 'right'):
                try:
                    dir_args[key] = int(val)
                except Exception:
                    dir_args[key] = None
            elif key == 'go':
                # go=100 -> grab next token if it's a direction
                try:
                    go_val = int(val)
                except Exception:
                    go_val = None
                dir_name = None
                if i + 1 < len(tokens) and tokens[i + 1] in ('up', 'down', 'left', 'right'):
                    dir_name = tokens[i + 1]
                    i += 1
                if dir_name is None:
                    dir_name = 'right'
                dir_args[dir_name] = (go_val if go_val is not None else None)
            i += 1
            continue

        # simple tokens: 'up', 'left', 'go', '100', 'right', etc
        if tok in ('up', 'down', 'left', 'right'):
            # if the next token is a number, consume it as a value
            if i + 1 < len(tokens) and tokens[i + 1].lstrip('-').isdigit():
                try:
                    val = int(tokens[i + 1])
                except Exception:
                    val = None
                dir_args[tok] = val
                i += 2
                continue
            else:
                dir_args[tok] = None
                i += 1
                continue

        if tok == 'go':
            # Look ahead: 'go right 100', 'go 100 right', 'go 100', 'go=100'
            dir_name = None
            amount = None
            if i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt in ('up', 'down', 'left', 'right'):
                    dir_name = nxt
                    if i + 2 < len(tokens) and tokens[i + 2].lstrip('-').isdigit():
                        amount = int(tokens[i + 2])
                        i += 3
                    else:
                        amount = None
                        i += 2
                elif nxt.lstrip('-').isdigit():
                    amount = int(nxt)
                    # optional direction after numeric
                    if i + 2 < len(tokens) and tokens[i + 2] in ('up', 'down', 'left', 'right'):
                        dir_name = tokens[i + 2]
                        i += 3
                    else:
                        dir_name = 'right'
                        i += 2
                else:
                    dir_name = 'right'
                    amount = None
                    i += 1
            else:
                dir_name = 'right'
                amount = None
                i += 1
            dir_args[dir_name] = amount
            continue

        # numeric standalone (e.g., '100' - assume right by default)
        if tok.lstrip('-').isdigit():
            try:
                amount = int(tok)
            except Exception:
                amount = None
            dir_args['right'] = amount
            i += 1
            continue

        # unrecognized token; ignore
        i += 1

    # Parse global step and margin overrides
    chosen_step = STEP_PIXELS
    for arg in sys.argv:
        if arg.startswith('--step=') or arg.startswith('step='):
            try:
                chosen_step = int(arg.split('=')[1])
            except ValueError:
                pass

    chosen_margin = MARGIN_PIXELS
    for arg in sys.argv:
        if arg.startswith('--margin=') or arg.startswith('margin='):
            try:
                chosen_margin = int(arg.split('=')[1])
            except ValueError:
                pass

    # Parse force flag from command line, and allow 'force=true' or '--force'
    force_flag = False
    for a in sys.argv:
        if a.lstrip('-').split('=', 1)[0] == 'force':
            # 'force' or 'force=true' or 'force=false'
            if '=' in a:
                try:
                    v = a.split('=', 1)[1].lower()
                    force_flag = not (v in ('0', 'false', 'no'))
                except Exception:
                    force_flag = True
            else:
                force_flag = True

    if len(dir_args) > 0:
        # Determine current position
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
            coords_inset = apply_margin(vectorListDiscrete, chosen_margin)
            currentX, currentY = coords_inset[current_index]

        # compute dx/dy requested
        dx = 0
        dy = 0
        for k, val in dir_args.items():
            step_val = chosen_step if val is None else val
            if k == 'up':
                dy += int(step_val)
            elif k == 'down':
                dy -= int(step_val)
            elif k == 'right':
                dx += int(step_val)
            elif k == 'left':
                dx -= int(step_val)

        # Compute the target. If force_flag is set, ignore margin clamping and only
        # clamp to absolute bounds. Otherwise, clamp to margin for safety.
        if force_flag:
            targetX = currentX if dx == 0 else clamp_to_bounds(currentX + dx, total_pixels)
            targetY = currentY if dy == 0 else clamp_to_bounds(currentY + dy, total_pixels)
        else:
            targetX = currentX if dx == 0 else clamp_to_margin(currentX + dx, chosen_margin, total_pixels)
            targetY = currentY if dy == 0 else clamp_to_margin(currentY + dy, chosen_margin, total_pixels)
        new_dx = targetX - currentX
        new_dy = targetY - currentY

        # Perform move
        if new_dx != 0 and new_dy != 0:
            move_both(new_dx, new_dy)
        elif new_dx != 0:
            if new_dx > 0:
                right(new_dx)
            else:
                left(abs(new_dx))
        elif new_dy != 0:
            if new_dy > 0:
                up(new_dy)
            else:
                down(abs(new_dy))

        stopAllMotor()
        # Update position file and try to update index if the new pos matches a known point
        coords_inset = apply_margin(vectorListDiscrete, chosen_margin)
        if not force_flag:
            idx = find_index_for_pos(coords_inset, targetX, targetY)
            if idx is not None:
                with open('current_index.txt', 'w') as f:
                    f.write(str(idx))
            save_position(targetX, targetY, coords_inset)
        else:
            # Force moves do not record position or update index per request.
            pass
        return

if __name__ == "__main__":
    main()
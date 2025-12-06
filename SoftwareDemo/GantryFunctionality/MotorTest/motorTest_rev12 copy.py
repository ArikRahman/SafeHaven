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

from gpiozero import DigitalOutputDevice
from rpi_hardware_pwm import HardwarePWM
from time import sleep, time
import sys
import os
import json
import tty
import termios
import select

# Force pin modes for RPi 5 (PWM pins to Alt0, Dir pins to Output)
# This ensures the pins are correctly muxed for the hardware PWM and GPIO control
os.system("pinctrl set 12 a0")
os.system("pinctrl set 13 a0")
os.system("pinctrl set 6 op")
os.system("pinctrl set 16 op")


# Define the GPIO pins
PUL_PIN_X = 13 # Pulse pin x-axis
DIR_PIN_X = 6  # Direction pins x-axis
PUL_PIN_Y = 12 # Pulse pin y-axis
DIR_PIN_Y = 16 # Direction pins y-axis


# Parameters
duty_cycle = 50  # 50% duty cycle for PWM (0-100)
f_x = 25600 # PWM frequency for X-axis in Hz (approx 40mm/s)
f_y = 25600 # PWM frequency for Y-axis in Hz (approx 40mm/s)
#i changed from 1600 to 6400 after changing driver microstep settings
steps_per_rev = 6400  # Microsteps per revolution for the motor, dictated by driver settings
length_per_rev = 10   # Length per revolution in mm
total_distance = 636  # Total traveling distance in mm for both axes
# total_pixels = 10000  # REMOVED - using mm directly
AXIS_MAX_MM = 636
MARGIN_MM = 20  # How far from the borders we want motions to stay (in mm)
STEP_MM = 20  # Default 'small' step used for direction-only commands

# X-axis speed calculations
speedX_rev_per_s = f_x / steps_per_rev  # Speed in revolutions per second
speedX_mm_per_s = (speedX_rev_per_s) * length_per_rev  # Speed in mm/s

# Y-axis speed calculations
speedY_rev_per_s = f_y / steps_per_rev  # Speed in revolutions per second
speedY_mm_per_s = (speedY_rev_per_s) * length_per_rev  # Speed in mm/s


def print_help():
    """Print usage information for the CLI and exit.

    The script supports a set of convenience commands and options used from
    the command line. We show short descriptions and several examples.
    """
    help_text = '''
Overview:
  motorTest_rev10.py - Control gantry motors from the command line.

Quick CLI usage examples:
  python3 motorTest_rev10.py next
  python3 motorTest_rev10.py origin --margin=20
  python3 motorTest_rev10.py up                            # default step
  python3 motorTest_rev10.py up=50                         # step=50mm
  python3 motorTest_rev10.py go right 100                 # shorthand
  python3 motorTest_rev10.py go 100 right                 # shorthand
  python3 motorTest_rev10.py --step=50 up                 # override global step
  python3 motorTest_rev10.py left=200 --force             # 'force' allows ignore margin clamp and prevents saving position
  python3 motorTest_rev10.py arcade                       # enter arcade mode
  python3 motorTest_rev10.py --help                       # show this help and exit

Main Commands:
  next             Move along the discrete vector list to the next vertical break
  origin           Move to origin (first coordinate in the vector list)
  reset            Recalibrate current position to the start of the vector list (Origin) without moving
  up/down/left/right [=mm]
                   Move that direction by either the optional mm amount or the default step size
  go [amount] <dir>
                   Shorthand for moving a specified amount in a direction; defaults to right
  arcade           Enter interactive arcade mode (keyboard-controlled)

Options:
  --step=<mm>      Override default step size
  --margin=<mm>    Override margin inset
  --force[=true|false]
                   Force moves outside margin and avoid saving position if true
  -h, --help       Print this help message

Notes:
  - Force moves do not update saved position or index unless CLI command explicitly writes one.
  - When using arcade mode, use WASD or arrow keys; space stops motors; q quits.
'''
    print(help_text)
    print(f"Gantry Config: {total_distance}mm")
    # print(f"Resolution: 1 pixel = {total_distance/total_pixels} mm")
    print("done")
    return


# Top-level short-circuit for help: print full usage and exit before hardware init.
if any(arg in ('-h', '--help', 'help') for arg in sys.argv[1:]):
    print_help()
    sys.exit(0)

# Initialize the pins as output devices
# Using rpi-hardware-pwm for hardware PWM on Pi 5 (Chip 0)
# GPIO 13 -> PWM0 (Channel 1)
# GPIO 12 -> PWM0 (Channel 0)
# Note: On this RPi 5, the RP1 PWM controller appears as pwmchip0.
pulX = HardwarePWM(pwm_channel=1, hz=f_x, chip=0)
dirX = DigitalOutputDevice(DIR_PIN_X, 
                           active_high=True)  # Active high to rotate CW
pulY = HardwarePWM(pwm_channel=0, hz=f_y, chip=0)
dirY = DigitalOutputDevice(DIR_PIN_Y, 
                           active_high=True)  # Active high to rotate CW


# Vector List (Raw 0-10000)
_vectorListContinuous_Raw = [(0, 10000), (0, 9915), 
                        (2094, 9915), (2094, 85), 
                        (2844, 85), (2844, 9915), 
                        (3594, 9915), (3594, 85), 
                        (4344, 85), (4344, 9915), 
                        (5094, 9915), (5094, 85), 
                        (5844, 85), (5844, 9915), 
                        (6594, 9915), (6594, 85), 
                        (7156, 85), (7156, 9915), 
                        (7156, 10000), (0, 10000)]
_vectorListDiscrete_Raw = [(0, 10000), (0, 9900), 
                      (2094, 9900), (2094, 7940), (2094, 5980), (2094, 4020), (2094, 2060), (2094, 100), 
                      (2844, 100), (2844, 2060), (2844, 4020), (2844, 5980), (2844, 7940), (2844, 9900), 
                      (3594, 9900), (3594, 7940), (3594, 5980), (3594, 4020), (3594, 2060), (3594, 100), 
                      (4344, 100), (4344, 2060), (4344, 4020), (4344, 5980), (4344, 7940), (4344, 9900), 
                      (5094, 9900), (5094, 7940), (5094, 5980), (5094, 4020), (5094, 2060), (5094, 100), 
                      (5844, 100), (5844, 2060), (5844, 4020), (5844, 5980), (5844, 7940), (5844, 9900), 
                      (6594, 9900), (6594, 7940), (6594, 5980), (6594, 4020), (6594, 2060), (6594, 100), 
                      (7156, 100), (7156, 2060), (7156, 4020), (7156, 5980), (7156, 7940), (7156, 9900), 
                      (7156, 10000), (0, 10000)]
_vectorListDiscrete_test_Raw = [(0, 10000), (0, 9900), 
                      (2094, 9900), (2094, 7940), (2094, 5980), (2094, 4020), (2094, 2060), (2094, 100), (2094, 9900),
                      (2844, 9900), (2844, 7940), (2844, 5980), (2844, 4020), (2844, 2060), (2844, 100), (2844, 9900), 
                      (3594, 9900), (3594, 7940), (3594, 5980), (3594, 4020), (3594, 2060), (3594, 100), (3594, 9900),
                      (4344, 9900), (4344, 7940), (4344, 5980), (4344, 4020), (4344, 2060), (4344, 100), (4344, 9900), 
                      (5094, 9900), (5094, 7940), (5094, 5980), (5094, 4020), (5094, 2060), (5094, 100), (5094, 9900),
                      (5844, 9900), (5844, 7940), (5844, 5980), (5844, 4020), (5844, 2060), (5844, 100), (5844, 9900), 
                      (6594, 9900), (6594, 7940), (6594, 5980), (6594, 4020), (6594, 2060), (6594, 100), (6594, 9900),
                      (7156, 9900), (7156, 7940), (7156, 5980), (7156, 4020), (7156, 2060), (7156, 100), (7156, 9900), 
                      (7156, 10000), (0, 10000)]

# Scale to mm
def scale_vec(v_list):
    return [(int(x * AXIS_MAX_MM / 10000), int(y * AXIS_MAX_MM / 10000)) for x, y in v_list]

vectorListContinuous = scale_vec(_vectorListContinuous_Raw)
vectorListDiscrete = scale_vec(_vectorListDiscrete_Raw)
vectorListDiscrete_test = scale_vec(_vectorListDiscrete_test_Raw)


def apply_margin(coords, margin=MARGIN_MM, max_val=AXIS_MAX_MM):
    """Clamp each coordinate pair inside the range [margin, max_val - margin].

    This keeps the gantry from traveling to the extreme border or outside it.
    """
    if margin <= 0:
        return coords
    inset = []
    for x, y in coords:
        # Ensure integer arithmetic; preserve integers from original coordinates
        cx = int(min(max(x, margin), max_val - margin))
        cy = int(min(max(y, margin), max_val - margin))
        inset.append((cx, cy))
    return inset


# Create inset (margined) variants of the travel vectors
vectorListContinuous_inset = apply_margin(vectorListContinuous, MARGIN_MM)
vectorListDiscrete_inset = apply_margin(vectorListDiscrete, MARGIN_MM)
vectorListDiscrete_test_inset = apply_margin(vectorListDiscrete_test, MARGIN_MM)


def up(dist_mm):
    #these are commands calling, using old library, want to swap out, not direction but everything else
    duration = abs(dist_mm)/speedY_mm_per_s
    # print(f"DEBUG: Moving UP {dist_mm} mm, duration {duration:.2f}s")
    dirY.on() # Set direction to CW
    pulY.start(duty_cycle)
    sleep(duration) # Seconds
    pulY.stop()

def down(dist_mm):
    duration = abs(dist_mm)/speedY_mm_per_s
    # print(f"DEBUG: Moving DOWN {dist_mm} mm, duration {duration:.2f}s")
    dirY.off() # Set direction to CCW
    pulY.start(duty_cycle)
    sleep(duration) # Seconds
    pulY.stop()

def right(dist_mm):
    duration = abs(dist_mm)/speedX_mm_per_s
    # print(f"DEBUG: Moving RIGHT {dist_mm} mm, duration {duration:.2f}s")
    dirX.on() # Set direction to CW
    pulX.start(duty_cycle)
    sleep(duration) # Seconds
    pulX.stop()

def left(dist_mm):
    duration = abs(dist_mm)/speedX_mm_per_s
    # print(f"DEBUG: Moving LEFT {dist_mm} mm, duration {duration:.2f}s")
    dirX.off() # Set direction to CCW
    pulX.start(duty_cycle)
    sleep(duration) # Seconds
    pulX.stop()

def stopX_Motor():
    pulX.stop()

def stopY_Motor():
    pulY.stop()

def stopAllMotor():
    stopX_Motor()
    stopY_Motor()

# Cleanup
def close():
    pulX.stop()
    dirX.close()
    pulY.stop()
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


def clamp_to_margin(value, margin=MARGIN_MM, max_val=AXIS_MAX_MM):
    return int(min(max(value, margin), max_val - margin))


def clamp_to_bounds(value, max_val=AXIS_MAX_MM):
    """Clamp to absolute bounds [0, max_val]."""
    return int(min(max(value, 0), max_val))


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
    timeX = abs(dx) / speedX_mm_per_s if dx != 0 else 0
    timeY = abs(dy) / speedY_mm_per_s if dy != 0 else 0
    max_time = max(timeX, timeY)

    print(f"Moving: dx={dx} ({timeX:.2f}s), dy={dy} ({timeY:.2f}s) @ {speedX_mm_per_s:.1f}mm/s. Total: {max_time:.2f}s")

    # start both
    if dx != 0:
        pulX.start(duty)
    if dy != 0:
        pulY.start(duty)

    start_time = time()

    def wait_with_countdown(duration):
        end_time = time() + duration
        while True:
            now = time()
            remaining_wait = end_time - now
            if remaining_wait <= 0:
                break
            
            # Mimic Arcade Mode: Refresh PWM state continuously
            # This can help dampen resonance or prevent timeouts if any exist
            if dx != 0: pulX.start(duty)
            if dy != 0: pulY.start(duty)
            
            # Sleep briefly to avoid 100% CPU usage, but fast enough to be responsive
            sleep(0.02)

    # if both times are >0 then coordinate stopping times
    if timeX > 0 and timeY > 0:
        # sleep until the shorter one finishes
        if timeX == timeY:
            wait_with_countdown(timeX)
            pulX.stop()
            pulY.stop()
        elif timeX > timeY:
            wait_with_countdown(timeY)
            # stop Y
            pulY.stop()
            # finish X
            wait_with_countdown(timeX - timeY)
            pulX.stop()
        else:
            # timeY > timeX
            wait_with_countdown(timeX)
            pulX.stop()
            wait_with_countdown(timeY - timeX)
            pulY.stop()

    # If we only need to move X or Y
    elif timeX > 0 and timeY == 0:
        wait_with_countdown(timeX)
        pulX.stop()
    elif timeY > 0 and timeX == 0:
        wait_with_countdown(timeY)
        pulY.stop()
    
    print(f"Move complete.                  ") # Clear line


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


def arcade_mode(initialX, initialY, step=STEP_MM, chosen_margin=MARGIN_MM, force_flag=False):
    """Interactive keyboard mode for arcade-style manual control.

    Use arrow keys or WASD for movement; 'q' to quit; 'f' to toggle force; 'p' to print current position.
    Each key press moves by `step` mm; use --step to customize when calling the script.
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
                targetX = currentX if dx == 0 else clamp_to_margin(currentX + dx, chosen_margin, AXIS_MAX_MM)
                targetY = currentY if dy == 0 else clamp_to_margin(currentY + dy, chosen_margin, AXIS_MAX_MM)

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

def start_motion_xy(dir_x, dir_y):
    """Start motor movement in X and Y directions (non-blocking).
    dir_x: 1 (right), -1 (left), 0 (stop)
    dir_y: 1 (up), -1 (down), 0 (stop)
    """
    # X Axis
    if dir_x == 1:
        dirX.on()
        pulX.start(duty_cycle)
    elif dir_x == -1:
        dirX.off()
        pulX.start(duty_cycle)
    else:
        pulX.stop()

    # Y Axis
    if dir_y == 1:
        dirY.on()
        pulY.start(duty_cycle)
    elif dir_y == -1:
        dirY.off()
        pulY.start(duty_cycle)
    else:
        pulY.stop()

def arcade_mode_live(initialX, initialY, chosen_margin=MARGIN_MM, force_flag=False):
    """
    Live arcade mode using terminal input (works over SSH/headless).
    Simulates 'hold-to-move' by using a watchdog timer on key repeats.
    Supports diagonal movement by tracking X and Y keys independently.
    """
    print('\nEntering LIVE arcade mode (terminal). Hold keys to move (WASD/Arrows). q to quit. p for pos.')
    
    currentX = float(initialX)
    currentY = float(initialY)
    
    # State tracking
    active_x = 0 # 0, 1, -1
    active_y = 0 # 0, 1, -1
    last_x_time = 0
    last_y_time = 0
    
    # Watchdog threshold: if no key for this long, stop that axis.
    # Increased to 0.5s to cover the initial keyboard repeat delay (usually ~500ms).
    STOP_THRESHOLD = 0.5 

    try:
        while True:
            # Short timeout to allow checking the watchdog
            k = read_key(timeout=0.02) # Faster polling for responsiveness
            now = time()
            
            # 1. Process Input
            if k is not None:
                if k in ('w', 'W', 'k') or k == '\x1b[A' or k == '\x1b[OA':
                    active_y = 1
                    last_y_time = now
                elif k in ('s', 'S', 'j') or k == '\x1b[B' or k == '\x1b[OB':
                    active_y = -1
                    last_y_time = now
                elif k in ('a', 'A', 'h') or k == '\x1b[D' or k == '\x1b[OD':
                    active_x = -1
                    last_x_time = now
                elif k in ('d', 'D', 'l') or k == '\x1b[C' or k == '\x1b[OC':
                    active_x = 1
                    last_x_time = now
                elif k in ('q', 'Q'):
                    break
                elif k in ('p', 'P'):
                    print(f'Pos: {int(currentX)}, {int(currentY)}')
            
            # 2. Check Watchdogs (Stop axis if key released)
            if active_x != 0 and (now - last_x_time) > STOP_THRESHOLD:
                active_x = 0
            if active_y != 0 and (now - last_y_time) > STOP_THRESHOLD:
                active_y = 0
            
            # 3. Update Motors
            start_motion_xy(active_x, active_y)
            
            # 4. Update Position (Dead reckoning)
            # We assume the loop runs fast enough that 'dt' is small.
            # Ideally we'd measure dt from last loop, but for simplicity we can just
            # accumulate based on active state over the loop duration?
            # Better: track time since last update.
            
            # Actually, let's just update position based on elapsed time since last loop iteration.
            # But we need a 'last_loop_time'.
            
            # Let's initialize last_loop_time before loop
            if 'last_loop_time' not in locals():
                last_loop_time = now
            
            dt = now - last_loop_time
            last_loop_time = now
            
            if active_x != 0:
                dist = dt * speedX_mm_per_s * active_x
                currentX += dist
            if active_y != 0:
                dist = dt * speedY_mm_per_s * active_y
                currentY += dist
            
            # 5. Safety Clamp
            limit = AXIS_MAX_MM if force_flag else (AXIS_MAX_MM - chosen_margin)
            lower = 0 if force_flag else chosen_margin
            
            hit_limit = False
            if currentX < lower: currentX = lower; hit_limit = True
            if currentX > limit: currentX = limit; hit_limit = True
            if currentY < lower: currentY = lower; hit_limit = True
            if currentY > limit: currentY = limit; hit_limit = True
            
            if hit_limit:
                # If we hit a limit, stop the motor pushing into it?
                # Simple approach: just stop everything if we hit a wall, or clamp pos.
                # If we clamp pos but motor keeps running, we lose steps.
                # Let's stop the specific axis that hit the limit.
                if (currentX <= lower and active_x == -1) or (currentX >= limit and active_x == 1):
                    active_x = 0
                if (currentY <= lower and active_y == -1) or (currentY >= limit and active_y == 1):
                    active_y = 0
                start_motion_xy(active_x, active_y)

    finally:
        stopAllMotor()
        print(f'Arcade mode stopped. Final Pos: {int(currentX)}, {int(currentY)}')
        # Save position on exit
        if not force_flag:
            coords_inset = apply_margin(vectorListDiscrete, chosen_margin)
            save_position(currentX, currentY, coords_inset)
        else:
            save_position(currentX, currentY)


def move_to_position_arcade_style(targetX, targetY, currentX, currentY):
    """
    Moves to target using the same control loop style as arcade_mode_live.
    This avoids the 'grating' sound reported with the calculated duration move_both.
    """
    print(f"Arcade-style move: ({int(currentX)}, {int(currentY)}) -> ({int(targetX)}, {int(targetY)})")
    
    # Time step for the loop (50Hz)
    dt = 0.02 
    
    # Tolerance in mm
    TOLERANCE = 2.0

    try:
        while True:
            # Calculate distance remaining
            dx = targetX - currentX
            dy = targetY - currentY
            
            # Check if we are close enough
            if abs(dx) < TOLERANCE and abs(dy) < TOLERANCE:
                break
            
            # Determine direction for this step
            step_x = 0
            if abs(dx) >= TOLERANCE:
                step_x = 1 if dx > 0 else -1
                
            step_y = 0
            if abs(dy) >= TOLERANCE:
                step_y = 1 if dy > 0 else -1
            
            # Apply motor command
            start_motion_xy(step_x, step_y)
            
            # Wait
            sleep(dt)
            
            # Update position (Dead reckoning)
            if step_x != 0:
                currentX += step_x * speedX_mm_per_s * dt
            if step_y != 0:
                currentY += step_y * speedY_mm_per_s * dt
            
            # Optional: Print progress every 0.5s? No, keep it silent/smooth.
            
    finally:
        stopAllMotor()
        
    return currentX, currentY


def facetrack_live_mode(initialX, initialY):
    """
    Live face tracking mode.
    Moves towards the target position from faceposition.json using a control loop.
    """
    print("Starting Live Face Tracking. Press Ctrl+C to stop.")
    
    currentX = float(initialX)
    currentY = float(initialY)
    
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../PiCamera/faceposition.json"))
    
    # Control loop parameters
    dt = 0.05 # 20Hz update rate
    DEADBAND = 10 # mm

    try:
        while True:
            # 1. Update Target from JSON
            try:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        # Coordinates are already averaged by the camera script now
                        raw_x = int(data['motor_coords']['x'])
                        raw_y = int(data['motor_coords']['y'])
                        
                        targetX = raw_x
                        targetY = raw_y
                        
                        # Apply Offset (Camera is centered 100mm to the left)
                        targetX += -100
                        
                        # Clamp
                        targetX = clamp_to_bounds(targetX)
                        targetY = clamp_to_bounds(targetY)
            except Exception:
                # Ignore read errors (file might be busy)
                pass
            
            # 2. Move towards target
            dx = targetX - currentX
            dy = targetY - currentY
            
            dir_x = 0
            dir_y = 0
            
            if abs(dx) > DEADBAND:
                dir_x = 1 if dx > 0 else -1
            
            if abs(dy) > DEADBAND:
                dir_y = 1 if dy > 0 else -1
                
            # Start/Update Motion
            start_motion_xy(dir_x, dir_y)
            
            # 3. Update Position Estimate
            if dir_x != 0:
                currentX += dir_x * speedX_mm_per_s * dt
            if dir_y != 0:
                currentY += dir_y * speedY_mm_per_s * dt
                
            # Clamp current position estimate
            currentX = max(0, min(currentX, AXIS_MAX_MM))
            currentY = max(0, min(currentY, AXIS_MAX_MM))
            
            # Print status occasionally or if moving
            if dir_x != 0 or dir_y != 0:
                 print(f"Tracking: Pos({int(currentX)}, {int(currentY)}) -> Target({int(targetX)}, {int(targetY)})   ", end='\r')
            
            sleep(dt)
            
    except KeyboardInterrupt:
        print("\nTracking stopped.")
    finally:
        stopAllMotor()
        return currentX, currentY


######### Main #########
def parse_speed(v):
    if v is None: return None
    s = str(v).lower()
    if s.endswith('mms'):
        try:
            return float(s[:-3])
        except:
            return None
    return None

def main():
    # Check for speed override first (applies to all modes)
    target_speed_mm_s = None
    for arg in sys.argv[1:]:
        # check for speed token (e.g. 40mms)
        # We need to handle 'speed=40mms' or just '40mms'
        if '=' in arg:
            key, val = arg.split('=', 1)
            if key == 'speed':
                s_val = parse_speed(val)
                if s_val is not None:
                    target_speed_mm_s = s_val
        else:
            # standalone token
            spd = parse_speed(arg.lstrip('-'))
            if spd is not None:
                target_speed_mm_s = spd

    # Apply speed override if present
    if target_speed_mm_s is not None:
        global f_x, f_y, speedX_rev_per_s, speedX_mm_per_s, speedX_pixels_per_s
        global speedY_rev_per_s, speedY_mm_per_s, speedY_pixels_per_s

        # Calculate new frequency
        # f = speed_mm_s * steps_per_mm
        # steps_per_mm = steps_per_rev / length_per_rev
        new_freq = int(target_speed_mm_s * (steps_per_rev / length_per_rev))
        
        print(f"DEBUG: Speed requested: {target_speed_mm_s} mm/s")
        print(f"DEBUG: New Frequency: {new_freq} Hz")
        
        # Update hardware PWM
        pulX.change_frequency(new_freq)
        pulY.change_frequency(new_freq)
        
        # Update global speed variables for sleep calculations
        f_x = new_freq
        f_y = new_freq
        
        speedX_rev_per_s = f_x / steps_per_rev
        speedX_mm_per_s = speedX_rev_per_s * length_per_rev
        # speedX_pixels_per_s = (speedX_mm_per_s / total_distance) * total_pixels
        
        speedY_rev_per_s = f_y / steps_per_rev
        speedY_mm_per_s = speedY_rev_per_s * length_per_rev
        # speedY_pixels_per_s = (speedY_mm_per_s / total_distance) * total_pixels
        
        print(f"DEBUG: Calculated Speed: {speedX_mm_per_s:.2f} mm/s")
    else:
        print(f"DEBUG: Default Speed: {speedX_mm_per_s:.2f} mm/s")

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
            coords_inset = apply_margin(vectorListDiscrete, MARGIN_MM)
            currentX, currentY = coords_inset[current_index]

        chosen_margin = MARGIN_MM
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

    if "facetrack" in sys.argv:
        print("DEBUG: Executing 'facetrack' command (Live)")
        
        # Determine current position
        pos_info = load_position()
        if pos_info and 'current_pos' in pos_info:
            currentX, currentY = pos_info['current_pos']
        else:
            # Fallback to index or 0
            if os.path.exists('current_index.txt'):
                with open('current_index.txt', 'r') as f:
                    try:
                        current_index = int(f.read().strip())
                    except Exception:
                        current_index = 0
            else:
                current_index = 0
            coords_inset = apply_margin(vectorListDiscrete, MARGIN_MM)
            currentX, currentY = coords_inset[current_index]

        # Run live tracking
        currentX, currentY = facetrack_live_mode(currentX, currentY)
        
        save_position(currentX, currentY)
        return

    # Priority order: next -> origin -> directional commands
    if "next" in sys.argv:
        print("DEBUG: Executing 'next' command")
        # Load current index
        if os.path.exists("current_index.txt"):
            with open("current_index.txt", "r") as f:
                current_index = int(f.read().strip())
        else:
            current_index = 0
        
        # Allow a custom margin to be passed as a command-line argument as
        # `margin=<pixels>` or `--margin=<pixels>`. If not, use the default MARGIN_MM.
        chosen_margin = MARGIN_MM
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
        print("DEBUG: Executing 'origin' command")
        # Bring gantry to the origin (approximate to the in-margin origin)
        chosen_margin = MARGIN_MM
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
        
        print(f"DEBUG: Origin move dx={dx}, dy={dy}")

        # Use arcade-style movement to avoid grating sound
        currentX, currentY = move_to_position_arcade_style(originX, originY, currentX, currentY)

        # stop and save new position (origin); update index to 0
        stopAllMotor()
        with open('current_index.txt', 'w') as f:
            f.write('0')
        save_position(originX, originY, coords_inset)
        return

    if "reset" in sys.argv:
        print("DEBUG: Executing 'reset' command")
        
        # Allow margin override for reset too, to match origin
        chosen_margin = MARGIN_MM
        for arg in sys.argv:
            if arg.startswith('--margin=') or arg.startswith('margin='):
                try:
                    chosen_margin = int(arg.split('=')[1])
                except ValueError:
                    pass

        coords_inset = apply_margin(vectorListDiscrete, chosen_margin)
        originX, originY = coords_inset[0]

        # Reset current position to the origin of the path
        save_position(originX, originY, coords_inset)
        with open('current_index.txt', 'w') as f:
            f.write('0')
        print(f"Position recalibrated to Origin ({originX}, {originY}).")
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
    target_speed_mm_s = None

    def parse_val(v):
        if v is None: return None
        s = str(v).lower()
        if s.endswith('mm'):
            try:
                return int(float(s[:-2]))
            except:
                return None
        try:
            return int(v)
        except:
            return None

    def is_val(s):
        return parse_val(s) is not None

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        
        # check for speed token (e.g. 40mms) - already handled globally but we need to skip it here
        spd = parse_speed(tok)
        if spd is not None:
            # target_speed_mm_s = spd # Already done
            i += 1
            continue

        # inline form like right=100
        if '=' in tok:
            key, val = tok.split('=', 1)
            if key in ('up', 'down', 'left', 'right'):
                dir_args[key] = parse_val(val)
            elif key == 'speed':
                # speed=40mms - already handled
                i += 1
                continue
            elif key == 'go':
                # go=100 -> grab next token if it's a direction
                go_val = parse_val(val)
                dir_name = None
                if i + 1 < len(tokens) and tokens[i + 1] in ('up', 'down', 'left', 'right'):
                    dir_name = tokens[i + 1]
                    i += 1
                if dir_name is None:
                    dir_name = 'right'
                dir_args[dir_name] = go_val
            i += 1
            continue

        # simple tokens: 'up', 'left', 'go', '100', 'right', etc
        if tok in ('up', 'down', 'left', 'right'):
            # if the next token is a value, consume it
            if i + 1 < len(tokens) and is_val(tokens[i + 1]):
                val = parse_val(tokens[i + 1])
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
                    if i + 2 < len(tokens) and is_val(tokens[i + 2]):
                        amount = parse_val(tokens[i + 2])
                        i += 3
                    else:
                        amount = None
                        i += 2
                elif is_val(nxt):
                    amount = parse_val(nxt)
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
        if is_val(tok):
            amount = parse_val(tok)
            dir_args['right'] = amount
            i += 1
            continue

        # unrecognized token; ignore
        i += 1

    # Parse global step and margin overrides
    chosen_step = STEP_MM
    for arg in sys.argv:
        if arg.startswith('--step=') or arg.startswith('step='):
            try:
                chosen_step = int(arg.split('=')[1])
            except ValueError:
                pass

    chosen_margin = MARGIN_MM
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

        # Compute the target. If force_flag is set, ignore ALL clamping (including bounds).
        # Otherwise, clamp to margin for safety.
        if force_flag:
            targetX = currentX + dx
            targetY = currentY + dy
        else:
            targetX = currentX if dx == 0 else clamp_to_margin(currentX + dx, chosen_margin, AXIS_MAX_MM)
            targetY = currentY if dy == 0 else clamp_to_margin(currentY + dy, chosen_margin, AXIS_MAX_MM)
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
    print("done")
# Revision 5 by Vincent
# Changes:
    # Control movement of gantry carriage with keyboard arrow keys
    # Inplement reed switches  

import curses
import time
from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
import RPi.GPIO as GPIO
from time import sleep

# Define GPIO Reed pins
# FIXME: change pins later
Reed_Pins = {
    "X_MIN": 1,
    "X_MAX": 2,
    "Y_MIN": 3,
    "Y_MAX": 4
}

# Reed sampling rate (how often to check)
Poll = 0.002 # 2ms

# Delay
Debounce = 0.01 # 10 ms

# Set up Reed GPIO
def initReed():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for name, pin in Reed_Pins.items():
        # Set as input with internal pull-up so it swings to LOW when triggered
        # Active LOW, normally open
        # Open (no magnet) = pulled HIGH
        # Closed (magnet) = LOW
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"[INIT] Reed {name} on GPIO{pin} set as INPUT with pull-up enabled")

def triggerLimit(motion: str) -> bool:
    """
    Return True if the limit switch for the given motion is currently active.
    motion is one of: "X_CW", "X_CCW", "Y_CW", "Y_CCW"
    """
    if motion == "X_CW":       # Moving right, watch X_MAX
        pin = Reed_Pins["X_MAX"]
    elif motion == "X_CCW":    # Moving left, watch X_MIN
        pin = Reed_Pins["X_MIN"]
    elif motion == "Y_CW":     # Moving up, watch Y_MAX
        pin = Reed_Pins["Y_MAX"]
    elif motion == "Y_CCW":    # Moving down, watch Y_MIN
        pin = Reed_Pins["Y_MIN"]
    else:
        return False  # Unknown motion

    # Active-LOW: LOW means magnet present / limit hit
    return GPIO.input(pin) == GPIO.LOW


def blockLimit(stdscr, motion: str) -> bool:
    """
    Check if the requested motion is blocked by an active limit.
    Returns True if motion is blocked (we should NOT start).
    """
    if triggerLimit(motion):
        stdscr.addstr(12, 0, f"[LIMIT] Motion {motion} blocked by limit switch")
        stdscr.clrtoeol()
        stdscr.refresh()
        stopMotor()
        return True
    return False


def monitorLimit(stdscr, motion: str) -> bool:
    """
    Called in the main loop while motor is running.
    If the limit is hit mid-move, stop and return True.
    """
    if motion is None:
        return False

    if triggerLimit(motion):
        stopMotor()
        stdscr.addstr(12, 0, f"[LIMIT] Hit limit during {motion}, stopping")
        stdscr.clrtoeol()
        stdscr.refresh()
        return True

    return False

# Define GPIO motor pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

# Motor config
duty_cycle = 0.50  # 50% duty cycle for PWM
motor_speed = 6769 # Speed of motor in frequency (Hz)
idle = 0 # Motor off
timeout = 0.15 # Seconds after last key event to stop

pulX = None
dirX = None
pulY = None
dirY = None

# Motor definitions
def initMotor():
    global pulX, dirX, pulY, dirY

    pulX = PWMOutputDevice(PUL_PIN_X, active_high=True, initial_value=idle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
    dirX = DigitalOutputDevice(DIR_PIN_X, active_high=True, pin_factory= None)  # Active high to rotate CW
    pulY = PWMOutputDevice(PUL_PIN_Y, active_high=True, initial_value=idle, frequency=motor_speed, pin_factory= None)  # PWM for pulse control
    dirY = DigitalOutputDevice(DIR_PIN_Y, active_high=True, pin_factory= None)  # Active high to rotate CW
    print("[INIT] Motors initialized")

def stopMotor():
    pulX.value = idle
    pulY.value = idle

def rightX(): # X CW
    dirX.off()
    pulX.value = duty_cycle

def leftX(): # X CCW
    dirX.on()
    pulX.value = duty_cycle

def upY(): # Y CW
    dirY.off()
    pulY.value = duty_cycle

def downY(): # Y CCW
    dirY.on()
    pulY.value = duty_cycle

def main(stdscr):
    curses.curs_set(0) # Hide cursor
    stdscr.nodelay(True) # Non-blocking get character
    stdscr.keypad(True) # Enable arrow key

    stdscr.clear()
    stdscr.addstr(0, 0, "Gantry Motor Movement Control (Arrow Keys, continuous)")
    stdscr.addstr(2, 0, "Controls:")
    stdscr.addstr(3, 2, "Up Arrow    -> Y CW (continuous)")
    stdscr.addstr(4, 2, "Down Arrow  -> Y CCW (continuous)")
    stdscr.addstr(5, 2, "Left Arrow  -> X CCW (continuous)")
    stdscr.addstr(6, 2, "Right Arrow -> X CW (continuous)")
    stdscr.addstr(8, 0, "Press 'q' to quit.")
    stdscr.refresh()

    currentMotion = None
    lastKeyTime = 0

    try:
        while True:
            key = stdscr.getch()
            now = time.time()

            if key != -1:
                if key == ord('q'):
                    break

                elif key == curses.KEY_UP:
                    stdscr.addstr(10, 0, "Y CW   (UP)    ")
                    stdscr.clrtoeol()
                    stdscr.refresh()
                    upY()
                    currentMotion = "Y_CW"
                    lastKeyTime = now

                elif key == curses.KEY_DOWN:
                    stdscr.addstr(10, 0, "Y CCW  (DOWN)  ")
                    stdscr.clrtoeol()
                    stdscr.refresh()
                    downY()
                    currentMotion = "Y_CCW"
                    lastKeyTime = now

                elif key == curses.KEY_LEFT:
                    stdscr.addstr(10, 0, "X CCW  (LEFT)  ")
                    stdscr.clrtoeol()
                    stdscr.refresh()
                    leftX()
                    currentMotion = "X_CCW"
                    lastKeyTime = now

                elif key == curses.KEY_RIGHT:
                    stdscr.addstr(10, 0, "X CW   (RIGHT) ")
                    stdscr.clrtoeol()
                    stdscr.refresh()
                    rightX()
                    currentMotion = "X_CW"
                    lastKeyTime = now

                else:
                    # Any other key doesn't move the motor
                    stopMotor()
                    currentMotion = None

            # Check limits while moving, stop if it reached limit
            if monitorLimit(stdscr, currentMotion):
                currentMotion = None

            # If moving but don't see a repeated key event assume the key is released and stop
            if currentMotion is not None and (now - lastKeyTime) > timeout:
                stopMotor()
                currentMotion = None
                stdscr.addstr(10, 0, "Idle            ")
                stdscr.clrtoeol()
                stdscr.refresh()

            time.sleep(0.01)
    finally:
        stopMotor()

if __name__ == "__main__":
    try:
        initMotor()
        initReed()
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt, exiting...")
    finally:
        if pulX is not None:
            pulX.close()
        if pulY is not None:
            pulY.close()
        if dirX is not None:
            dirX.close()
        if dirY is not None:
            dirY.close()
        print("[CLEANUP] GPIO cleared")
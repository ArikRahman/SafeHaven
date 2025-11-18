# Revision 5 by Vincent
# Changes:
#     Control movement of gantry carriage with keyboard arrow keys

import curses
import time
from gpiozero import OutputDevice, DigitalOutputDevice, PWMOutputDevice
from time import sleep

# Define the GPIO pins
PUL_PIN_X = 13    # Pulse pin x-axis
DIR_PIN_X = 6     # Direction pins x-axis
PUL_PIN_Y = 12    # Pulse pin y-axis
DIR_PIN_Y = 16    # Direction pins y-axis

# Motor config
duty_cycle = 0.50  # 50% duty cycle for PWM
motor_speed = 100 # Speed of motor in frequency (Hz)
idle = 0 # Motor off
timeout = 0.15 # Seconds after last key event to stop

pulX = None
dirX = None
pulY = None
dirY = None

# Definitions
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
                    stdscr.refresh()
                    upY()
                    currentMotion = "Y_CW"
                    lastKeyTime = now

                elif key == curses.KEY_DOWN:
                    stdscr.addstr(10, 0, "Y CCW  (DOWN)  ")
                    stdscr.refresh()
                    downY()
                    currentMotion = "Y_CCW"
                    lastKeyTime = now

                elif key == curses.KEY_LEFT:
                    stdscr.addstr(10, 0, "X CCW  (LEFT)  ")
                    stdscr.refresh()
                    leftX()
                    currentMotion = "X_CCW"
                    lastKeyTime = now

                elif key == curses.KEY_RIGHT:
                    stdscr.addstr(10, 0, "X CW   (RIGHT) ")
                    stdscr.refresh()
                    rightX()
                    currentMotion = "X_CW"
                    lastKeyTime = now

                else:
                    # Any other key doesn't move the motor
                    stopMotor()
                    currentMotion = None

                # If moving but don't see a repeated key event assume the key is released and stop
                if currentMotion is not None and (now - lastKeyTime) > timeout:
                    stopMotor()
                    currentMotion = None
                    stdscr.addstr(10, 0, "Idle            ")
                    stdscr.refresh()

                time.sleep(0.01)
    finally:
        stopMotor()

if __name__ == "__main__":
    try:
        initMotor()
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
# Reed switch program

# Using normally open (NO) Reed switches. Activates when magnet are in proximity (~1.5cm distance to trigger magnet)

# Wiring: Normally Open (NO) reed switch between GPIO pin and GND
# Internal pull-up keeps pin HIGH when open, LOW when magnet closes
# Wires are non-polar. Either can go into GND or digital pin

# Run command:
# python 3 /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/LimitSwitches/ReedSwitches.py

import time
import gpiozero
from MotorTest import motorTest_rev7 as motor

# GPIO pin assignments
Reed_Pins = {
    "X_MIN": 17,
    "X_MAX": 27,
    "Y_MIN": 22,
    "Y_MAX": 23,
}

# Loop settings
POLL_RATE = 0.005    # 5 ms scan interval
DEBOUNCE  = 0.010    # 10 ms debounce

# Create objects
reeds = {
    name: gpiozero.Button(
        pin,
        pull_up=True,   # LOW when magnet closes
        bounce_time=DEBOUNCE
    )
    for name, pin in Reed_Pins.items()
}

def ReedMonitor():
    print("Starting ReedMonitor()... watching X_MIN, X_MAX, Y_MIN, Y_MAX")
    last_state = {name: reeds[name].is_pressed for name in reeds}

    try:
        while True:
            for name, sw in reeds.items():
                state = sw.is_pressed   # True when switch closed (magnet present)

                if state != last_state[name]:
                    ts = time.strftime("%H:%M:%S")

                    if state:
                        print(f"[{ts}] {name} TRIGGERED")

                        # Stop appropriate axis
                        if name in ("X_MIN", "X_MAX"):
                            motor.stopX_Motor()     
                        if name in ("Y_MIN", "Y_MAX"):
                            motor.stopY_Motor()    

                        # This block is optional and redundant but guarantees both axis are stopped
                        x_hit = reeds["X_MIN"].is_pressed or reeds["X_MAX"].is_pressed
                        y_hit = reeds["Y_MIN"].is_pressed or reeds["Y_MAX"].is_pressed
                        if x_hit and y_hit:
                            motor.stopAllMotor()

                    else:
                        print(f"[{ts}] {name} RELEASED")

                    last_state[name] = state

            time.sleep(POLL_RATE)

    except KeyboardInterrupt:
        print("\nReedMonitor() stopped by user.")

def home():
    print("Starting homing sequence to (0, 10000)")

    # Move to origin
    motor.left(10000)   
    motor.up(10000)     

    x_homed = False
    y_homed = False

    try:
        while True:
            # Check if X_MIN is reached
            if not x_homed and reeds["X_MIN"].is_pressed:
                print("X_MIN hit. Stopping X axis")
                motor.stopX_Motor()
                x_homed = True

            # Check if Y_MAX is reached
            if not y_homed and reeds["Y_MAX"].is_pressed:
                print("Y_MAX hit. Stopping Y axis")
                motor.stopY_Motor()
                y_homed = True

            # If both axes homed, stop everything and exit
            if x_homed and y_homed:
                print("Both axes homed. Stopping all motors")
                motor.stopAllMotor()
                break

            time.sleep(POLL_RATE)

    except KeyboardInterrupt:
        print("\nHoming interrupted by user.")
        motor.stopAllMotor()

    motor.close()

def main():
    try:
        ReedMonitor()
        # home()

    except KeyboardInterrupt:
        print("\nExiting reed switch monitor.")

if __name__ == "__main__":
    main()
# import time
# from gpiozero import Button

# reed = Button(23, pull_up=True)  # GPIO 23 and GND

# while True:
#     print("pressed" if reed.is_pressed else "released")
#     time.sleep(0.2)

# Reed switch program

# Using normally open (NO) Reed switches. Activates when magnet are in proximity (~1.5cm distance to trigger magnet)

# Wiring: Normally Open (NO) reed switch between GPIO pin and GND
# Internal pull-up keeps pin HIGH when open, LOW when magnet closes.

import time
import gpiozero

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

def stopMotor(axis_name):
    print(f"*** STOP MOTOR: limit reached on {axis_name}! ***")
    # TODO: insert real motor-stop command here

def main():
    # Setup reed switches using internal pull-up
    reeds = {
        name: gpiozero.Button(
            pin,
            pull_up=True,          # HIGH normally, LOW when magnet closes
            bounce_time=DEBOUNCE
        )
        for name, pin in Reed_Pins.items()
    }

    print("=== Reed Switch Safety Monitor (Pi 5) ===")
    print("Wiring: NO switch -> GPIO <--> GND (internal pull-up enabled)")
    print("Trigger = switch closes (magnet), GPIO pulled LOW")
    print()

    # Track last state so it only print changes
    last_state = {name: None for name in reeds}

    try:
        while True:
            for name, sw in reeds.items():
                state = sw.is_pressed  # True when switch closed (magnet detected)

                # Only print or stop motors when state changes
                if state != last_state[name]:
                    ts = time.strftime("%H:%M:%S")

                    if state:
                        print(f"[{ts}] {name} TRIGGERED")
                        stopMotor(name)
                    else:
                        print(f"[{ts}] {name} RELEASED")

                    last_state[name] = state

            time.sleep(POLL_RATE)

    except KeyboardInterrupt:
        print("\nExiting reed switch monitor.")

if __name__ == "__main__":
    main()
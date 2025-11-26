from gpiozero import Button
import time

# ================================
# CONFIG
# ================================
STOP_BUTTON_PIN = 24   # Your stop button GPIO
DEBOUNCE = 0.05        # 50ms debounce (optional)


# ================================
# MOTOR STOP FUNCTION
# ================================
def stop_motors():
    """
    Place your motor-shutdown code here.
    This is called immediately when the stop button is pressed.
    """
    print(">>> STOP BUTTON PRESSED � stopping motors now!")
    # -----------------------------------------
    # TODO: insert your motor stop code here
    # e.g., pulX.value = 0, pulY.value = 0, etc.
    # -----------------------------------------


# ================================
# STOP BUTTON WATCHER
# ================================
def monitor_stop_button():
    """
    Continuously checks the stop button.
    When pressed, calls stop_motors().
    This runs forever unless you break manually.
    """
    stop_button = Button(STOP_BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE)

    print("Stop button monitor active. Press button to trigger stop.")

    while True:
        if stop_button.is_pressed:
            stop_motors()
            break

        time.sleep(0.01)    # 10ms polling rate � safe & responsive


# ================================
# MAIN
# ================================
def main():
    try:
        monitor_stop_button()
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()

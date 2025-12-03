from gpiozero import Button
import time
from MotorTest import motorTest_rev7 as motor
from GantryFunctionality import RunState

STOP_BUTTON_PIN = 24   # Stop button pin on GPIO 24
DEBOUNCE = 0.05        # 50ms debounce 

# Run command
# python3 /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/GantryFunctionality/ShutoffSwitch/EmergencyStop.py

# Monitor for stop button press
def monitorStopPress():
    # Create object
    stop_button = Button(STOP_BUTTON_PIN, pull_up=True, bounce_time=DEBOUNCE)

    print("Stop button monitor active. Press button to trigger stop.")

    try:
        while True:
            if stop_button.is_pressed:
                # Stop motor when button is pressed
                motor.stopAllMotor()
                RunState.stop_flag.set()
                break
            
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nExiting program.")

def main():    
    monitorStopPress()
    
if __name__ == "__main__":
    main()
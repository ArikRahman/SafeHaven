# main.py
import matplotlib.pyplot as plt
import threading

# import SoftwareDemo.GantryFunctionality.MotorFunc.motorFunc as moFo
from GantryFunctionality.MotorTest import motorTest_rev7 as moFo
from PiCamera import PiCameraAI as PiCamAI
from GantryFunctionality.LimitSwitches import ReedSwitches as Reed
from GantryFunctionality.ShutoffSwitch import EmergencyStop as Shutoff
from SnakepathAlgorithm import SnakePathGen as sp 
from GantryFunctionality import RunState

# Command to run PiCamera script
# source ~/yolo-env/bin/activate && python3 /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/main.py

def main():
    # Start safety monitors
    # Start thread to monitor Reed sensors
    reed_thread = threading.Thread(target=Reed.ReedMonitor, daemon=True)
    reed_thread.start()
    print("Reed Monitor actively running in the background...")

    # Start thread to monitor if stop button is pressed
    stop_thread = threading.Thread(target=Shutoff.monitorStopPress,daemon=True)
    stop_thread.start()
    print("Monitor emergency stop button...")

    # Run primary functional programs
    PiCamAI.PersonCapture()         # Open PiCamera and detect humans

    # Check if abort initiated after camera step
    if RunState.stop_flag.is_set():
        print("Abort requested (stop flag set) after PiCamera. Cleaning up.")
        moFo.stopAllMotor()
        moFo.close()
        return
    
    # Generate snake path from latest box_coords.json (written by PiCameraAI)
    (
        pathlist,
        start_range,
        snake_range,
        return_range,
        invert_count,
        gantry_box,
        origin_x,
        origin_y,
    ) = sp.generate_path_from_detection()  
    
    # Check if abort initated before gantry movement
    if RunState.stop_flag.is_set():
        print("Abort requested before motion. Cleaning up.")
        moFo.stopAllMotor()
        moFo.close()
        return

    if 0:
        # Optional plot of snakepath
        plt.figure(figsize=(6, 6)) # Size of generated output

        sp.plot_segment(pathlist, start_range, 'green', 'Start Path')
        sp.plot_segment(pathlist, snake_range, 'blue', 'Snake Path')
        sp.plot_segment(pathlist, return_range, 'purple', 'Return Path')

        plt.plot(origin_x, origin_y, 'ro') # Origin point on plot
        plt.annotate("Origin", (origin_x - .05, 1.5 + .04)) # Plot origin plot
        plt.xlim(-0.1, 1.5 + 0.1) # Define X-limits
        plt.ylim(-0.1, 1.5 + 0.1) # Define Y-limits
        plt.xlabel("X (meters)") # X-axis label
        plt.ylabel("Y (meters)") # Y-axis label
        plt.title("Snake Path Scan") # Title
        plt.minorticks_on() # Turn on minor ticks
        plt.grid()
        plt.legend()
        plt.show()

    # Safety stop (start off)
    moFo.stopAllMotor()

    # Start motor movement and follow snakepath
    moFo.followSnakepath(pathlist)

    # Check if abort initated after gantry movement
    if RunState.stop_flag.is_set():
        print("Abort requested during/after motion. Skipping homing/plotting.")
        moFo.stopAllMotor()
        moFo.close()
        return

    # Conclude run
    moFo.close()
    print("Run complete...")

if __name__ == "__main__":
    main()

def PathGenAscii():
    # __/\\\\\\\\\\\\\_________________________________/\\\_____________/\\\\\\\\\\\\______________________________        
    #  _\/\\\/////////\\\______________________________\/\\\___________/\\\//////////_______________________________       
    #   _\/\\\_______\/\\\____________________/\\\______\/\\\__________/\\\__________________________________________      
    #    _\/\\\\\\\\\\\\\/___/\\\\\\\\\_____/\\\\\\\\\\\_\/\\\_________\/\\\____/\\\\\\\_____/\\\\\\\\___/\\/\\\\\\___     
    #     _\/\\\/////////____\////////\\\___\////\\\////__\/\\\\\\\\\\__\/\\\___\/////\\\___/\\\/////\\\_\/\\\////\\\__    
    #      _\/\\\_______________/\\\\\\\\\\_____\/\\\______\/\\\/////\\\_\/\\\_______\/\\\__/\\\\\\\\\\\__\/\\\__\//\\\_   
    #       _\/\\\______________/\\\/////\\\_____\/\\\_/\\__\/\\\___\/\\\_\/\\\_______\/\\\_\//\\///////___\/\\\___\/\\\_  
    #        _\/\\\_____________\//\\\\\\\\/\\____\//\\\\\___\/\\\___\/\\\_\//\\\\\\\\\\\\/___\//\\\\\\\\\\_\/\\\___\/\\\_ 
    #         _\///_______________\////////\//______\/////____\///____\///___\////////////______\//////////__\///____\///__
    return 0

def GantryAscii():
    # _____/\\\\\\\\\\\\________________________________________________________________________        
    #  ___/\\\//////////_________________________________________________________________________       
    #   __/\\\______________________________________________/\\\_______________________/\\\__/\\\_      
    #    _\/\\\____/\\\\\\\__/\\\\\\\\\_____/\\/\\\\\\____/\\\\\\\\\\\__/\\/\\\\\\\____\//\\\/\\\__     
    #     _\/\\\___\/////\\\_\////////\\\___\/\\\////\\\__\////\\\////__\/\\\/////\\\____\//\\\\\___    
    #      _\/\\\_______\/\\\___/\\\\\\\\\\__\/\\\__\//\\\____\/\\\______\/\\\___\///______\//\\\____   
    #       _\/\\\_______\/\\\__/\\\/////\\\__\/\\\___\/\\\____\/\\\_/\\__\/\\\__________/\\_/\\\_____  
    #        _\//\\\\\\\\\\\\/__\//\\\\\\\\/\\_\/\\\___\/\\\____\//\\\\\___\/\\\_________\//\\\\/______ 
    #         __\////////////_____\////////\//__\///____\///______\/////____\///___________\////________
    return 0

# # Initialize motors and execute movement along generated snake path
# moFo.motor_init()
# moFo.motor_move(path, step_size='1/8')

def PlotAscii():
    # __/\\\\\\\\\\\`\\____/\\\\\\_______________________________________________________________________________        
    #  _\/\\\/////////\\\_\////\\\_______________________________________________________________________________       
    #   _\/\\\_______\/\\\____\/\\\______________________/\\\__________/\\\_______/\\\_________________/\\\\\\\\__      
    #    _\/\\\\\\\\\\\\\/_____\/\\\________/\\\\\_____/\\\\\\\\\\\__/\\\\\\\\\\\_\///___/\\/\\\\\\____/\\\////\\\_     
    #     _\/\\\/////////_______\/\\\______/\\\///\\\__\////\\\////__\////\\\////___/\\\_\/\\\////\\\__\//\\\\\\\\\_    
    #      _\/\\\________________\/\\\_____/\\\__\//\\\____\/\\\_________\/\\\______\/\\\_\/\\\__\//\\\__\///////\\\_   
    #       _\/\\\________________\/\\\____\//\\\__/\\\_____\/\\\_/\\_____\/\\\_/\\__\/\\\_\/\\\___\/\\\__/\\_____\\\_  
    #        _\/\\\______________/\\\\\\\\\__\///\\\\\/______\//\\\\\______\//\\\\\___\/\\\_\/\\\___\/\\\_\//\\\\\\\\__ 
    #         _\///_`_____________\/////////_____\/////_________\/////________\/////____\///__\///____\///___\////////___
    return 0
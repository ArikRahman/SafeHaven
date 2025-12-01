import SoftwareDemo.GantryFunctionality.MotorFunc.motorFunc as moFo
import matplotlib.pyplot as plt
from PiCamera import PiCameraAI as PiCamAI
from GantryFunctionality.LimitSwitches import ReedSwitches as Reed
from GantryFunctionality.ShutoffSwitch import EmergencyStop as Shutoff
from SnakepathAlgorithm import SnakePathGen as sp 

# Command to run PiCamera script
# source ~/yolo-env/bin/activate && python3 /home/corban/Documents/GitHub/SafeHaven/SoftwareDemo/main.py

def main():
    PiCamAI.PersonCapture()         # Open PiCamera and detect humans
    Reed.ReedMonitor()              # Actively scan and monitor reed switch state and stop motors
    Shutoff.monitorStopPress()      # Monitor for when stop button is pressed
    sp.generate_snake_path_gantry() # Generate snake path
    moFo.                           # Gantry movement execution
    Reed.home()                     # Send gantry carriage to origin (0,10000)

if __name__ == "__main__":
    main()


# __/\\\\\\\\\\\\\_________________________________/\\\_____________/\\\\\\\\\\\\______________________________        
#  _\/\\\/////////\\\______________________________\/\\\___________/\\\//////////_______________________________       
#   _\/\\\_______\/\\\____________________/\\\______\/\\\__________/\\\__________________________________________      
#    _\/\\\\\\\\\\\\\/___/\\\\\\\\\_____/\\\\\\\\\\\_\/\\\_________\/\\\____/\\\\\\\_____/\\\\\\\\___/\\/\\\\\\___     
#     _\/\\\/////////____\////////\\\___\////\\\////__\/\\\\\\\\\\__\/\\\___\/////\\\___/\\\/////\\\_\/\\\////\\\__    
#      _\/\\\_______________/\\\\\\\\\\_____\/\\\______\/\\\/////\\\_\/\\\_______\/\\\__/\\\\\\\\\\\__\/\\\__\//\\\_   
#       _\/\\\______________/\\\/////\\\_____\/\\\_/\\__\/\\\___\/\\\_\/\\\_______\/\\\_\//\\///////___\/\\\___\/\\\_  
#        _\/\\\_____________\//\\\\\\\\/\\____\//\\\\\___\/\\\___\/\\\_\//\\\\\\\\\\\\/___\//\\\\\\\\\\_\/\\\___\/\\\_ 
#         _\///_______________\////////\//______\/////____\///____\///___\////////////______\//////////__\///____\///__

# Generate snake path
path, start_range, snake_range, return_range = sp.generate_snake_path_gantry(
    x_min=0.2584, y_min=0.0988, 
    x_max=0.8384, y_max=1.5, 
    step_x=8/100 , step_y=3/100, 
    origin_x=0, origin_y=1.5
    )

# _____/\\\\\\\\\\\\________________________________________________________________________        
#  ___/\\\//////////_________________________________________________________________________       
#   __/\\\______________________________________________/\\\_______________________/\\\__/\\\_      
#    _\/\\\____/\\\\\\\__/\\\\\\\\\_____/\\/\\\\\\____/\\\\\\\\\\\__/\\/\\\\\\\____\//\\\/\\\__     
#     _\/\\\___\/////\\\_\////////\\\___\/\\\////\\\__\////\\\////__\/\\\/////\\\____\//\\\\\___    
#      _\/\\\_______\/\\\___/\\\\\\\\\\__\/\\\__\//\\\____\/\\\______\/\\\___\///______\//\\\____   
#       _\/\\\_______\/\\\__/\\\/////\\\__\/\\\___\/\\\____\/\\\_/\\__\/\\\__________/\\_/\\\_____  
#        _\//\\\\\\\\\\\\/__\//\\\\\\\\/\\_\/\\\___\/\\\____\//\\\\\___\/\\\_________\//\\\\/______ 
#         __\////////////_____\////////\//__\///____\///______\/////____\///___________\////________

# Initialize motors and execute movement along generated snake path
moFo.motor_init()
moFo.motor_move(path, step_size='1/8')

# __/\\\\\\\\\\\\\____/\\\\\\_______________________________________________________________________________        
#  _\/\\\/////////\\\_\////\\\_______________________________________________________________________________       
#   _\/\\\_______\/\\\____\/\\\______________________/\\\__________/\\\_______/\\\_________________/\\\\\\\\__      
#    _\/\\\\\\\\\\\\\/_____\/\\\________/\\\\\_____/\\\\\\\\\\\__/\\\\\\\\\\\_\///___/\\/\\\\\\____/\\\////\\\_     
#     _\/\\\/////////_______\/\\\______/\\\///\\\__\////\\\////__\////\\\////___/\\\_\/\\\////\\\__\//\\\\\\\\\_    
#      _\/\\\________________\/\\\_____/\\\__\//\\\____\/\\\_________\/\\\______\/\\\_\/\\\__\//\\\__\///////\\\_   
#       _\/\\\________________\/\\\____\//\\\__/\\\_____\/\\\_/\\_____\/\\\_/\\__\/\\\_\/\\\___\/\\\__/\\_____\\\_  
#        _\/\\\______________/\\\\\\\\\__\///\\\\\/______\//\\\\\______\//\\\\\___\/\\\_\/\\\___\/\\\_\//\\\\\\\\__ 
#         _\///______________\/////////_____\/////_________\/////________\/////____\///__\///____\///___\////////___

# Plot the snake path
plt.figure(figsize=(6, 6)) # Size of generated output

sp.plot_segment(path, start_range, 'green', 'Start Path')
sp.plot_segment(path, snake_range, 'blue', 'Snake Path')
sp.plot_segment(path, return_range, 'purple', 'Return Path')

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
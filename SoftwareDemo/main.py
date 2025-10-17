spa = __import__('SnakePathAlgorithm.SnakePathAlgorithm_V1.3.SnakePathAlgorithm')
import SoftwareDemo.GantryFunctionality.MotorFunc.motorFunc as moFo
import matplotlib.pyplot as plt

# Generate snake path
path, start_range, snake_range, return_range = spa.generate_snake_path(
    x_min=0.2584, y_min=0.0988, 
    x_max=0.8384, y_max=1.5, 
    step_x=8/100 , step_y=3/100, 
    origin_x=0, origin_y=1.5
    )


# Initialize motors and execute movement along generated snake path
moFo.motor_init()
moFo.motor_move(path, step_size='1/8')


# Plot the snake path
plt.figure(figsize=(6, 6)) # Size of generated output

spa.plot_segment(path, start_range, 'green', 'Start Path')
spa.plot_segment(path, snake_range, 'blue', 'Snake Path')
spa.plot_segment(path, return_range, 'purple', 'Return Path')

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
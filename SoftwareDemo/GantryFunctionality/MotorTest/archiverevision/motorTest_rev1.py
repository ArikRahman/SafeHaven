from gpiozero import Motor
from time import sleep

PathList = []

motor_x = Motor(forward=4, backward=14, pwm=True)
motor_y = Motor(forward=5, backward=15, pwm=True)

def MotorSteer(dest_x, dest_y):
    current_x, current_y = get_pos()
    if dest_y != current_y:
        motor_y.forward()
        sleep((current_y-dest_y)/speed_y())
        motor_y.forward(0)
    elif dest_x != current_x:
        motor_x.forward()
        sleep((current_x-dest_x)/speed_x())
        motor_x.forward(0)

while True:
    MotorSteer(from_Path_Gen_x(), from_Path_Gen_y())

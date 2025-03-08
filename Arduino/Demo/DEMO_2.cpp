// Define stepper motor connections:
#define dirPinx 8
#define stepPinx 7
#define dirPiny 6
#define stepPiny 5
#define stepPinp 9
// include libraries
#include <Stepper.h>

int speed = 250;
int motor_speed = 250;

int x_steps = 4;
int y_steps = 5;
int arm_steps = 2;

int y_stepsize = 1000;
int x_stepsize = 1000;
int arm_stepsize = 1000;

bool y_dir = false;

void setup() {
  // Declare pins as output:
  pinMode(stepPinx, OUTPUT);
  pinMode(dirPinx, OUTPUT);
  pinMode(stepPiny, OUTPUT);
  pinMode(dirPiny, OUTPUT);
  pinMode(stepPinp, OUTPUT);
  // Set the spinning direction CW/CCW: high is clockwise
  digitalWrite(dirPinx, HIGH);
  digitalWrite(dirPiny, HIGH);
}

void loop() {
  
  // box();
  y_motion();
  // xy_motion();
  // while(1); // hang on completion
}

void frame() {
  digitalWrite(stepPinp, HIGH);
  delay(40);
  digitalWrite(stepPinp, LOW);
  delay(40);
}

void step_x(bool dir) {
  // Set the direction (HIGH = clockwise, LOW = counterclockwise)
  if (dir) {
    digitalWrite(dirPinx, HIGH); // clockwise
  }
  else {
    digitalWrite(dirPinx, LOW); //counterclockwise
  }
  
  // Create a single step:
  digitalWrite(stepPinx, HIGH);
  delayMicroseconds(motor_speed);  // Adjust this value to control the speed
  digitalWrite(stepPinx, LOW);
  delayMicroseconds(motor_speed);  // This delay ensures proper timing between steps
}

void step_y(bool dir) {
  // Set the direction (HIGH = clockwise, LOW = counterclockwise)
  if (dir) {
    digitalWrite(dirPiny, HIGH); // clockwise
  }
  else {
    digitalWrite(dirPiny, LOW); //counterclockwise
  }
  
  // Create a single step:
  digitalWrite(stepPiny, HIGH);
  delayMicroseconds(motor_speed);  // Adjust this value to control the speed
  digitalWrite(stepPiny, LOW);
  delayMicroseconds(motor_speed);  // This delay ensures proper timing between steps
}

void move_x(bool dir) {
  for (int i=0; i<x_stepsize; i++) {
    step_x(dir);
  }
}

void move_y(bool dir) {
  for (int i=0; i<y_stepsize; i++) {
    step_y(dir);
  }
}

void reset_xy() {
  // reset x axis
  for(int i=0; i<x_steps; i++) {
    // step x motor
    move_x(true);
  }
  // reset y axis
  if(y_dir) {
    for(int i=0; i<y_steps; i++) {
      // step y motor
      move_y(y_dir);
    }
  }
}

void y_motion() {
  for(int i=0; i<y_steps; i++) {
    // signal radar board to capture a frame
    frame();
    delay(speed); // delay before moving
    // step Y motor
    move_y(y_dir);
    delay(speed); // delay after moving
  }

  // signal radar board to capture last frame
  frame();
  y_dir = !(y_dir); // change direction
  delay(speed); // delay before moving
}

void xy_motion() {
  for(int i=0; i<x_steps; i++) {
    // do Y motion
    y_motion();

    // step X motor
    move_x(false);
    delay(speed);
  }
  // do final Y motion
  y_motion();
  reset_xy(); // reset x-y motors to original position
}

void box() { // testing purposes
  move_x(true);
  delay(1000);
  move_y(true);
  delay(1000);

  move_x(false);
  delay(1000);
  move_y(false);
  delay(1000);
}
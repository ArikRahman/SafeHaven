// Define stepper motor connections:
#define dirPinx 8
#define stepPinx 7
#define dirPiny 6
#define stepPiny 5
#define stepPinp 9

// include libraries
#include <Stepper.h>

// 2.75s horizontal
// 1.5s vertical

// ***** USER SETTINGS ***** 
int speed = 1000; // delay speeds (delay, lower is faster)
int motor_speed = 100; // motor speed (delay, lower is faster)

int x_steps = 51; // ~20cm
int y_steps = 25; // ~10cm
int y_stepsize = 500; // ~2mm
int x_stepsize = 500; // ~2mm

bool discrete = false; // continuous or discrete movement
bool hardware_trig = false; // software or hardware trigger
bool y_down = false; // true = down, false = up
bool x_right = true; // true = right, false = left
// ***** USER SETTINGS ***** 

// GLOABL VARIABLES
bool y_start; // variable for storing y start direction
bool x_start; // variable for storing x start direction

void setup() {
  // Declare pins as output:
  pinMode(stepPinx, OUTPUT);
  pinMode(dirPinx, OUTPUT);
  pinMode(stepPiny, OUTPUT);
  pinMode(dirPiny, OUTPUT);
  pinMode(stepPinp, OUTPUT);
  // Set the spinning direction CW/CCW: high is clockwise
  digitalWrite(dirPinx, HIGH); // HIGH = right, LOW = 
  digitalWrite(dirPiny, HIGH);
  // Set all pin states
  digitalWrite(stepPinx, LOW);
  digitalWrite(stepPiny, LOW);
  digitalWrite(stepPinp, LOW);

  delay(5000); // delay 5s on start
}

void loop() {
  x_start = x_right; // store x start direction
  y_start = y_down; // store y start direction

  // box(); // countdown
  // countdown();
  xy_motion();
  // yx_motion();

  // ~20cm back and forth (w/ 500 microstepsize & 200 motor speed)
  // ~5.5s per horizontal motion -> ~cm/s = mm/s
  // for (int j=0; j<2; j++) {
  //   for (int i=0; i<51; i++) move_right();
  //   delay(1000);
  //   for (int i=0; i<51; i++) move_left();
  //   delay(1000);
  // } 

  // ~10cm back and forth (w/ 500 microstepsize & 200 motor speed)
  // ~s per vertical motion -> ~cm/s = mm/s
  // for (int j=0; j<2; j++) {
  //   for (int i=0; i<25; i++) move_up();
  //   delay(1000);
  //   for (int i=0; i<25; i++) move_down();
  //   delay(1000);
  // }

  // max x-axis range
  // int y_stepsize = 1000; // ~6cm
  // int x_stepsize = 1000; // ~6cm
  // for (int i=0; i<35; i++) move_right(); // go right
  // delay(1000);
  // for (int i=0; i<35; i++) move_left(); // go left


  // for manual scanner positioning
  // for (int i=0; i<1; i++) move_left();
  // for (int i=0; i<6; i++) move_left();
  // for (int i=0; i<1; i++) move_up();
  // for (int i=0; i<2; i++) move_down();

  // delay(3000);
  while(1); // hang on completion
}

void frame() { // this sends a pulse to the radar board hardware trigger
  digitalWrite(stepPinp, HIGH);
  delayMicroseconds(50);
  digitalWrite(stepPinp, LOW);
  delayMicroseconds(50);
}

void step_x(bool dir) { // true = right, false = left
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

void step_y(bool dir) { // true = down, false = up
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

void move_x(bool dir) { // true = right, false = left
  for (int i=0; i<x_stepsize; i++) {
    step_x(dir);
  }
}

void move_y(bool dir) { // true = down, false = up
  for (int i=0; i<y_stepsize; i++) {
    step_y(dir);
  }
}

// helper functions
void move_right() { move_x(true); }
void move_left() { move_x(false); }
void move_up() { move_y(false); }
void move_down() { move_y(true); }

void y_motion() { // this executes a low level y motion
  for(int i=0; i<y_steps; i++) {
    // signal radar board to capture a frame
    if (hardware_trig) frame();
    if (discrete) delay(speed); // delay before moving
    // step Y motor
    move_y(y_down);
    if (discrete) delay(speed); // delay after moving
  }

  // signal radar board to capture last frame
  if (hardware_trig) frame();
  y_down = !(y_down); // change direction
  if (discrete) delay(speed); // delay before moving
}

void x_motion() { // this executes a low level x motion
  for(int i=0; i<x_steps; i++) {
    // signal radar board to capture a frame
    if (hardware_trig) frame();
    if (discrete) delay(speed); // delay before moving
    // step Y motor
    move_x(x_right);
    if (discrete) delay(speed); // delay after moving
  }

  // signal radar board to capture last frame
  if (hardware_trig) frame();
  x_right = !(x_right); // change direction
  if (discrete) delay(speed); // delay before moving
}

void reset_yx() { // this resets an xy-axis scan moving vertically first
  // reset x axis
  for(int i=0; i<x_steps; i++) {
    // step x motor
    move_x(!x_start);
  }
  // reset y axis
  if(y_start != y_down) {
    for(int i=0; i<y_steps; i++) {
      // step y motor
      move_y(y_down);
    }
  }
}

void reset_xy() { // this resets an xy-axis scan moving horizontally first
  // reset y axis
  for(int i=0; i<y_steps; i++) {
    // step y motor
    move_y(!y_start);
  }
  // reset x axis
  if(x_start != x_right) { // new?
    for(int i=0; i<x_steps; i++) {
      // step x motor
      move_x(x_right);
    }
  }

  // if(x_right) { // OG
  //   for(int i=0; i<x_steps; i++) {
  //     // step x motor
  //     move_x(x_right);
  //   }
  // }
}

void yx_motion() { // this is an xy-axis scan moving vertically first
  for(int i=0; i<x_steps; i++) {
    // do Y motion
    y_motion();

    // step X motor
    move_x(x_right);
    if (discrete) delay(speed);
  }
  // do final Y motion
  y_motion();
  reset_yx(); // reset x-y motors to original position
}

void xy_motion() { // this is an xy-axis scan moving horizontally first
  for(int i=0; i<y_steps; i++) {
    // do Y motion
    x_motion();

    // step X motor
    move_y(y_down);
    if (discrete) delay(speed);
  }
  // do final Y motion
  x_motion();
  reset_xy(); // reset x-y motors to original position
}

void box() { // for testing purposes
  for (int i=0; i<4; i++) move_right();
  if (discrete) delay(speed);
  for (int i=0; i<4; i++) move_up();
  if (discrete) delay(speed);
  for (int i=0; i<4; i++) move_left();
  if (discrete) delay(speed);
  for (int i=0; i<4; i++) move_down();
  if (discrete) delay(speed);
}

void countdown() { // for testing purposes
  for (int i=0; i<4; i++) move_right();
  delay(250);
  for (int i=0; i<4; i++) move_up();
  delay(250);
  for (int i=0; i<4; i++) move_left();
  delay(250);
  for (int i=0; i<4; i++) move_down();
  delay(250);
}
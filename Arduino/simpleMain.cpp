// Define motor directions (from target's view towards front of scanner)
#define RIGHT HIGH
#define LEFT LOW
#define UP LOW
#define DOWN HIGH

// Define stepper motor connections
#define dirPinx 8
#define stepPinx 7
#define dirPiny 6
#define stepPiny 5
#define stepPinp 9

// Include libraries
#include <Stepper.h>

// ***** USER SETTINGS ***** 
int speed = 1000;       // ms delay speed for discrete motions
int motor_speed = 100;  // us delay for motor speed (lower is faster)
bool discrete = false;  // Continuous or discrete movement
bool hardware_trig = false; // Hardware or software trigger
bool y_dir = UP;     // true = down, false = up
bool x_dir = RIGHT;   // true = right, false = left
// ***** USER SETTINGS ***** 

// **** Define SAR scan **** //
// 25,000 microsteps = ~20cm
int x_steps = 400; // number X-axis of steps
int y_steps = 25; // number Y-axis of steps      
int y_stepsize = 250; // number of microsteps in each Y step
int x_stepsize = 62; // number of microsteps in each X step

// GLOBAL VARIABLES
bool y_start; // Stores y start direction
bool x_start; // Stores x start direction

void setup() {
  // Declare pins as output
  pinMode(stepPinx, OUTPUT); pinMode(dirPinx, OUTPUT);
  pinMode(stepPiny, OUTPUT); pinMode(dirPiny, OUTPUT);
  pinMode(stepPinp, OUTPUT);

  // Set default directions
  digitalWrite(dirPinx, x_dir);
  digitalWrite(dirPiny, y_dir);

  // Initialize motor state
  digitalWrite(stepPinx, LOW);
  digitalWrite(stepPiny, LOW);
  digitalWrite(stepPinp, LOW);

  delay(5000); // Initial delay for setup
}

void loop() {
  x_start = x_dir;   // Store initial X direction
  y_start = y_dir;    // Store initial Y direction

  ROM();         // Countdown or debug delay before start
  xy_motion();         // Execute scanning motion

  // move_right(int n); delay(speed);
  // move_left(int n); delay(speed);
  // move_up(int n); delay(speed);
  // move_down(int n); delay(speed);

  // delay(speed);
  while(1);            // Hang on completion
}

// Step function for a single motor step
void step_motor(bool dir, int stepPin, int dirPin) {
  digitalWrite(dirPin, dir); // Set direction
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(motor_speed);
  digitalWrite(stepPin, LOW);
  delayMicroseconds(motor_speed);
}

// Move function for multiple steps
void move_motor(bool dir, int steps, int stepPin, int dirPin) {
  for (int i = 0; i < steps; i++) {
    step_motor(dir, stepPin, dirPin);
  }
}

// Trigger function for the radar board
void frame() {
  digitalWrite(stepPinp, HIGH);
  delayMicroseconds(40);
  digitalWrite(stepPinp, LOW);
  delayMicroseconds(40);
}

// X motion handler
void x_motion() {
  for (int i = 0; i < x_steps; i++) {
    if (hardware_trig) frame();         // Trigger radar
    if (discrete) delay(speed);         // Delay for discrete motion
    move_motor(x_dir, x_stepsize, stepPinx, dirPinx);
    if (discrete) delay(speed);         // Delay for discrete motion
  }
  if (hardware_trig) frame();         // Trigger radar
  if (discrete) delay(speed);         // Delay for discrete motion
  x_dir = !x_dir;                   // Reverse direction
}

// Y motion handler
void y_motion() {
  for (int i = 0; i < y_steps; i++) {
    if (hardware_trig) frame();         // Trigger radar
    if (discrete) delay(speed);         // Delay for discrete motion
    move_motor(y_dir, y_stepsize, stepPiny, dirPiny);
    if (discrete) delay(speed);         // Delay for discrete motion
  }
  if (hardware_trig) frame();         // Trigger radar
  if (discrete) delay(speed);         // Delay for discrete motion
  y_dir = !y_dir;                     // Reverse direction
}

// Execute horizontal-first scanning pattern
void xy_motion() {
  for (int i = 0; i < y_steps; i++) {
    x_motion();                         // Perform X motion
    move_motor(y_dir, y_stepsize, stepPiny, dirPiny); // Step in Y direction
    if (discrete) delay(speed);         // Delay if discrete
  }
  x_motion();                           // Final X motion
  reset_xy();                           // Reset motors to initial position
}

// Reset function for horizontal-first scanning
void reset_xy() {
  // Reset Y axis
  for (int i = 0; i < y_steps; i++) {
    move_motor(!y_start, y_stepsize, stepPiny, dirPiny);
  }

  // Reset X axis if needed
  if (x_start != x_dir) {
    for (int i = 0; i < x_steps; i++) {
      move_motor(!x_start, x_stepsize, stepPinx, dirPinx);
    }
  }
}

// Range of Motion
void ROM() {
  move_motor(RIGHT, x_steps*x_stepsize, stepPinx, dirPinx);
  delay(speed);
  move_motor(UP, y_steps*y_stepsize, stepPiny, dirPiny);
  delay(speed);
  move_motor(LEFT, x_steps*x_stepsize, stepPinx, dirPinx);
  delay(speed);
  move_motor(DOWN, y_steps*y_stepsize, stepPiny, dirPiny);
  delay(speed);
}

// helper functions
void move_right(int n) { move_motor(RIGHT, n*x_stepsize, stepPinx, dirPinx); }
void move_left(int n) { move_motor(LEFT, n*x_stepsize, stepPinx, dirPinx); }
void move_up(int n) { move_motor(UP, n*y_stepsize, stepPiny, dirPiny); }
void move_down(int n) { move_motor(DOWN, n*y_stepsize, stepPiny, dirPiny); }
// This is the original code for DEMO 1

// stepper 1
#define STEPPER_PIN_1 0
#define STEPPER_PIN_2 1
#define STEPPER_PIN_3 2
#define STEPPER_PIN_4 3
// stepper 2
#define STEPPER_PIN_5 4
#define STEPPER_PIN_6 5
#define STEPPER_PIN_7 6
#define STEPPER_PIN_8 7
// stepper 3
#define STEPPER_PIN_9 8
#define STEPPER_PIN_10 9
#define STEPPER_PIN_11 10
#define STEPPER_PIN_12 11

// settings
int y_steps = 2;
int x_steps = 2;
int arm_steps = 2;

int y_stepsize = 200;
int x_stepsize = 200;
int arm_stepsize = 200;

int speed = 200;
int step_speed = 3;

// global vars
int step_number_x = 0;
int step_number_y = 0;
int step_number_arm = 0;
bool y_dir = false;

void setup() {
  pinMode(STEPPER_PIN_1, OUTPUT);
  pinMode(STEPPER_PIN_2, OUTPUT);
  pinMode(STEPPER_PIN_3, OUTPUT);
  pinMode(STEPPER_PIN_4, OUTPUT);

  pinMode(STEPPER_PIN_5, OUTPUT);
  pinMode(STEPPER_PIN_6, OUTPUT);
  pinMode(STEPPER_PIN_7, OUTPUT);
  pinMode(STEPPER_PIN_8, OUTPUT);

  pinMode(STEPPER_PIN_9, OUTPUT);
  pinMode(STEPPER_PIN_10, OUTPUT);
  pinMode(STEPPER_PIN_11, OUTPUT);
  pinMode(STEPPER_PIN_12, OUTPUT);

  pinMode(LED_BUILTIN, OUTPUT);
}

// // example
// void loop() {
  
//   for(int i=0; i<1000; i++) {
//     step_y(false);
//     step_x(false);
//     step_arm(false);
//     delay(step_speed);
//   }
//   delay(1000);
//   for(int i=0; i<1000; i++) {
//     step_y(true);
//     step_x(true);
//     step_arm(true);
//     delay(step_speed);
//   }
//   delay(1000);
// }


// main loop
void loop() {
  y_dir = false;

  // motion
  // y_motion();
  // x_motion();
  arm_motion();

  

  delay(2000);
}


void frame() {
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(speed);                      // wait for a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
  delay(speed);                      // wait for a second
}

void reset_xy() {
  // reset x axis
  for(int i=0; i<x_steps; i++) {
    // step X motor
    for(int j=0; j<x_stepsize; j++) {
      step_x(true);
      delay(step_speed);
    }
  }
  // reset y axis
  if(y_dir) {
    for(int i=0; i<y_steps; i++) {
      // step X motor
      for(int j=0; j<y_stepsize; j++) {
        step_y(y_dir);
        delay(step_speed);
      }
    }
  }
}

void reset_arm() {
  // reset arm position
  for(int i=0; i<arm_steps; i++) {
    // step X motor
    for(int j=0; j<arm_stepsize; j++) {
      step_arm(true);
      delay(step_speed);
    }
  }
}

void step_y(bool dir) {
  if(dir) {
    switch(step_number_x) {
      case 0:
        digitalWrite(STEPPER_PIN_1, HIGH);
        digitalWrite(STEPPER_PIN_2, LOW);
        digitalWrite(STEPPER_PIN_3, LOW);
        digitalWrite(STEPPER_PIN_4, LOW);
        break;
      case 1:
        digitalWrite(STEPPER_PIN_1, LOW);
        digitalWrite(STEPPER_PIN_2, HIGH);
        digitalWrite(STEPPER_PIN_3, LOW);
        digitalWrite(STEPPER_PIN_4, LOW);
        break;
      case 2:
        digitalWrite(STEPPER_PIN_1, LOW);
        digitalWrite(STEPPER_PIN_2, LOW);
        digitalWrite(STEPPER_PIN_3, HIGH);
        digitalWrite(STEPPER_PIN_4, LOW);
        break;
      case 3:
        digitalWrite(STEPPER_PIN_1, LOW);
        digitalWrite(STEPPER_PIN_2, LOW);
        digitalWrite(STEPPER_PIN_3, LOW);
        digitalWrite(STEPPER_PIN_4, HIGH);
        break;
      } 
  }
  else {
    switch(step_number_x) {
      case 0:
        digitalWrite(STEPPER_PIN_1, LOW);
        digitalWrite(STEPPER_PIN_2, LOW);
        digitalWrite(STEPPER_PIN_3, LOW);
        digitalWrite(STEPPER_PIN_4, HIGH);
        break;
      case 1:
        digitalWrite(STEPPER_PIN_1, LOW);
        digitalWrite(STEPPER_PIN_2, LOW);
        digitalWrite(STEPPER_PIN_3, HIGH);
        digitalWrite(STEPPER_PIN_4, LOW);
        break;
      case 2:
        digitalWrite(STEPPER_PIN_1, LOW);
        digitalWrite(STEPPER_PIN_2, HIGH);
        digitalWrite(STEPPER_PIN_3, LOW);
        digitalWrite(STEPPER_PIN_4, LOW);
        break;
      case 3:
        digitalWrite(STEPPER_PIN_1, HIGH);
        digitalWrite(STEPPER_PIN_2, LOW);
        digitalWrite(STEPPER_PIN_3, LOW);
        digitalWrite(STEPPER_PIN_4, LOW);
    } 
  }
  step_number_x++;
  if(step_number_x > 3){
    step_number_x = 0;
  }
}

void step_x(bool dir) {
  if(dir) {
    switch(step_number_y) {
      case 0:
        digitalWrite(STEPPER_PIN_5, HIGH);
        digitalWrite(STEPPER_PIN_6, LOW);
        digitalWrite(STEPPER_PIN_7, LOW);
        digitalWrite(STEPPER_PIN_8, LOW);
        break;
      case 1:
        digitalWrite(STEPPER_PIN_5, LOW);
        digitalWrite(STEPPER_PIN_6, HIGH);
        digitalWrite(STEPPER_PIN_7, LOW);
        digitalWrite(STEPPER_PIN_8, LOW);
        break;
      case 2:
        digitalWrite(STEPPER_PIN_5, LOW);
        digitalWrite(STEPPER_PIN_6, LOW);
        digitalWrite(STEPPER_PIN_7, HIGH);
        digitalWrite(STEPPER_PIN_8, LOW);
        break;
      case 3:
        digitalWrite(STEPPER_PIN_5, LOW);
        digitalWrite(STEPPER_PIN_6, LOW);
        digitalWrite(STEPPER_PIN_7, LOW);
        digitalWrite(STEPPER_PIN_8, HIGH);
        break;
      } 
  }
  else {
    switch(step_number_y) {
      case 0:
        digitalWrite(STEPPER_PIN_5, LOW);
        digitalWrite(STEPPER_PIN_6, LOW);
        digitalWrite(STEPPER_PIN_7, LOW);
        digitalWrite(STEPPER_PIN_8, HIGH);
        break;
      case 1:
        digitalWrite(STEPPER_PIN_5, LOW);
        digitalWrite(STEPPER_PIN_6, LOW);
        digitalWrite(STEPPER_PIN_7, HIGH);
        digitalWrite(STEPPER_PIN_8, LOW);
        break;
      case 2:
        digitalWrite(STEPPER_PIN_5, LOW);
        digitalWrite(STEPPER_PIN_6, HIGH);
        digitalWrite(STEPPER_PIN_7, LOW);
        digitalWrite(STEPPER_PIN_8, LOW);
        break;
      case 3:
        digitalWrite(STEPPER_PIN_5, HIGH);
        digitalWrite(STEPPER_PIN_6, LOW);
        digitalWrite(STEPPER_PIN_7, LOW);
        digitalWrite(STEPPER_PIN_8, LOW);
    } 
  }
  step_number_y++;
  if(step_number_y > 3){
    step_number_y = 0;
  }
}

void step_arm(bool dir) {
  if(dir) {
    switch(step_number_arm) {
      case 0:
        digitalWrite(STEPPER_PIN_9, HIGH);
        digitalWrite(STEPPER_PIN_10, LOW);
        digitalWrite(STEPPER_PIN_11, LOW);
        digitalWrite(STEPPER_PIN_12, LOW);
        break;
      case 1:
        digitalWrite(STEPPER_PIN_9, LOW);
        digitalWrite(STEPPER_PIN_10, HIGH);
        digitalWrite(STEPPER_PIN_11, LOW);
        digitalWrite(STEPPER_PIN_12, LOW);
        break;
      case 2:
        digitalWrite(STEPPER_PIN_9, LOW);
        digitalWrite(STEPPER_PIN_10, LOW);
        digitalWrite(STEPPER_PIN_11, HIGH);
        digitalWrite(STEPPER_PIN_12, LOW);
        break;
      case 3:
        digitalWrite(STEPPER_PIN_9, LOW);
        digitalWrite(STEPPER_PIN_10, LOW);
        digitalWrite(STEPPER_PIN_11, LOW);
        digitalWrite(STEPPER_PIN_12, HIGH);
        break;
      } 
  }
  else {
    switch(step_number_arm) {
      case 0:
        digitalWrite(STEPPER_PIN_9, LOW);
        digitalWrite(STEPPER_PIN_10, LOW);
        digitalWrite(STEPPER_PIN_11, LOW);
        digitalWrite(STEPPER_PIN_12, HIGH);
        break;
      case 1:
        digitalWrite(STEPPER_PIN_9, LOW);
        digitalWrite(STEPPER_PIN_10, LOW);
        digitalWrite(STEPPER_PIN_11, HIGH);
        digitalWrite(STEPPER_PIN_12, LOW);
        break;
      case 2:
        digitalWrite(STEPPER_PIN_9, LOW);
        digitalWrite(STEPPER_PIN_10, HIGH);
        digitalWrite(STEPPER_PIN_11, LOW);
        digitalWrite(STEPPER_PIN_12, LOW);
        break;
      case 3:
        digitalWrite(STEPPER_PIN_9, HIGH);
        digitalWrite(STEPPER_PIN_10, LOW);
        digitalWrite(STEPPER_PIN_11, LOW);
        digitalWrite(STEPPER_PIN_12, LOW);
    } 
  }
  step_number_arm++;
  if(step_number_arm > 3){
    step_number_arm = 0;
  }
}

void y_motion() {
  for(int i=0; i<y_steps; i++) {
    // signal radar board to capture a frame
    frame();
    delay(speed); // delay before moving

    // step Y motor
    for(int j=0; j<y_stepsize; j++) {
      step_y(y_dir);
      delay(step_speed);
    }
    delay(speed); // delay after moving
  }

  // signal radar board to capture last frame
  frame();
  y_dir = !(y_dir); // change direction
  delay(speed); // delay before moving
}

void x_motion() {
  for(int i=0; i<x_steps; i++) {
    // do Y motion
    y_motion();

    // step X motor
    for(int j=0; j<x_stepsize; j++) {
      step_x(false);
      delay(step_speed);
    }
    delay(speed);
  }
  // do final Y motion
  y_motion();
  reset_xy(); // reset x-y motors to original position
}

void arm_motion() {
  for(int i=0; i<arm_steps; i++) {

    // do X motion
    x_motion();

    // step 0 motor
    for(int j=0; j<arm_stepsize; j++) {
      step_arm(false);
      delay(step_speed);
    }
    delay(speed);

    // Reset y_dir to ensure Y always starts moving in the same direciton
    y_dir = false;
  }
  // do final X motion
  x_motion();
  reset_arm(); // reset arm to original position
}



// This is a heavily transcribed version of the code from the previous capstone group
// The logic of both programs are the same, I did my very best to keep the theme of the original program
// I have placed all original comments in parenthesis and starred ---> ex: // (*OG comments*) 

// Define stepper motor connections (Vertical steps):
#define dirPinx 8
#define stepPinx 7
#define dirPiny 6
#define stepPiny 5
#define stepPinp 9

// Define stepper motor connections (Horizontal steps):
// #define dirPinx 6
// #define stepPinx 5
// #define dirPiny 8
// #define stepPiny 7
// #define stepPinp 9

// include libraries
#include <Stepper.h>


int stepsPerRevolution;

void setup() {
  // (*Declare pins as output:*)
  pinMode(stepPinx, OUTPUT);
  pinMode(dirPinx, OUTPUT);
  pinMode(stepPiny, OUTPUT);
  pinMode(dirPiny, OUTPUT);
  pinMode(stepPinp, OUTPUT);
  // (*Set the spinning direction CW/CCW: high is clockwise*)
  digitalWrite(dirPinx, HIGH);
  digitalWrite(dirPiny, HIGH);
  // Set all pin states
  digitalWrite(stepPinx, LOW);
  digitalWrite(stepPiny, LOW);
  digitalWrite(stepPinp, LOW);
  delay(10000); // delay 10s for mmWave studio 'begin capture'
}

void loop() {
  // Execute a SAR scan using IWR1443BOOST
  for (int i=0; i<50; i++) {
    y_down(); // move the scanner down
    x_over(); // move the scanner horizontally
    y_up(); // move the scanner up
    x_over(); // move the scanner horizontally
  }
  cleanup(); // cleanup code (of some sort)
  while(1); // hang on completion
}

void frame() { // this function sends a pulse to the radar board signaling the hardware trigger
  digitalWrite(stepPinp, HIGH);
  delayMicroseconds(40);
  digitalWrite(stepPinp, LOW);
  delayMicroseconds(40);
}

void y_step() { // this function completes a single step in the Y direction
  digitalWrite(stepPiny, HIGH);
  delayMicroseconds(250);
  digitalWrite(stepPiny, LOW);
  delayMicroseconds(250);
}

void x_step() { // this function completes a single step in the X direction
  digitalWrite(stepPinx, HIGH);
  delayMicroseconds(250);
  digitalWrite(stepPinx, LOW);
  delayMicroseconds(250);
}

void y_down() { // This function completes a Y movement downwards 
  stepsPerRevolution = 28; // (*this is for 1 micro step 200 pulses per revolution =  2 full revolutions for this code. This precisely goes 20 cm*)
  digitalWrite(dirPiny, HIGH); // set the direction of the Y stepper motor downwards
  for(int j = 0; j<400; j++) {
    frame(); // signal harware trigger
    for (int i=0; i < stepsPerRevolution; i++) y_step(); // 28 microsteps = 1 revolution
  }
}

void x_over() { // This function completes a X movement in one direction
  stepsPerRevolution = 41;
  for(int f = 0; f<3; f++) {
    for (int i=0; i < stepsPerRevolution; i++) x_step(); // 41 microsteps = 1 revolution
    //delay(500); // (*CHANGE THIS LINE to change continuinity (continuous or not)*)
  }
}

void y_up() { // This function completes a Y movement upwards
  stepsPerRevolution = 28;
  digitalWrite(dirPiny, LOW); // set the direction of the Y stepper motor upwards
  for(int h = 0; h<400; h++) {
    frame();
    for (int i=0; i < stepsPerRevolution; i++) y_step(); // 28 microsteps = 1 revolution
  }
}

void cleanup() { // This function is some sort of cleanup code, I didn't quite understand the purpose so I left this as is
  digitalWrite(dirPiny, LOW); // set the direction of Y stepper motor upwards
  for(int g = 0; g<1; g++) {
    for (int i=0; i < stepsPerRevolution; i++) { // 28 microsteps = 1 revolution
      // take a y step
      digitalWrite(stepPiny, HIGH);
      delayMicroseconds(500);
      digitalWrite(stepPiny, LOW);
      delayMicroseconds(500);
    }
    digitalWrite(stepPiny, LOW);
    digitalWrite(dirPinx, HIGH);
    //delay(500); // (*CHANGE THIS LINE to change continuinity (continuous or not)*)
  }
  digitalWrite(stepPinx, LOW);
  digitalWrite(stepPiny, LOW);
}
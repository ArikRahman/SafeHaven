// This is the original code from the previous capstone group (w fixed spacing)

// Define stepper motor connections:
#define dirPinx 8
#define stepPinx 7
#define dirPiny 6
#define stepPiny 5
#define stepPinp 9
// include libraries
#include <Stepper.h>


int stepsPerRevolution;
bool completion = false;
int tracker;


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
  delay(10000);
}

void loop() {
  if(completion == false) {
    stepsPerRevolution = 28; // this is for 1 micro step 200 pulses per revolution =  2 full revolutions for this code. This precisely goes 20 cm
    // These four lines result in 1 step:
    for(int j = 0; j<400; j++) {
      digitalWrite(stepPinp, HIGH);
      delayMicroseconds(40);
      digitalWrite(stepPinp, LOW);
      delayMicroseconds(40);
      for (int i=0; i < stepsPerRevolution; i++){
        digitalWrite(stepPiny, HIGH);
        delayMicroseconds(250);
        digitalWrite(stepPiny, LOW);
        delayMicroseconds(250);
        digitalWrite(stepPinx, LOW);
      }
    
    //delay(100);
    digitalWrite(stepPinx, LOW);
    }

    for(int f = 0; f<3; f++) {
      stepsPerRevolution = 41;
      for (int i=0; i < stepsPerRevolution; i++) {
        digitalWrite(stepPinx, HIGH);
        delayMicroseconds(250);
        digitalWrite(stepPinx, LOW);
        delayMicroseconds(250);
      }
      digitalWrite(stepPiny, LOW);
      digitalWrite(dirPiny, LOW);
      //delay(500); // CHANGE THIS LINE to change continuinity (continuous or not)
    }
    for(int h = 0; h<400; h++) {
      stepsPerRevolution = 28;
      digitalWrite(stepPinp, HIGH);
      delayMicroseconds(40);
      digitalWrite(stepPinp, LOW);
      delayMicroseconds(40);
      for (int i=0; i < stepsPerRevolution; i++){
        digitalWrite(stepPiny, HIGH);
        delayMicroseconds(250);
        digitalWrite(stepPiny, LOW);
        delayMicroseconds(250);
      } 
      //delay(100);
      digitalWrite(stepPinx, LOW);
    }
    for(int g = 0; g<3; g++) {
      stepsPerRevolution = 41;
      for (int i=0; i < stepsPerRevolution; i++) {
        digitalWrite(stepPinx, HIGH);
        delayMicroseconds(250);
        digitalWrite(stepPinx, LOW);
        delayMicroseconds(250);
      }
      digitalWrite(stepPiny, LOW);
      digitalWrite(dirPiny, HIGH);
      //delay(500); // CHANGE THIS LINE to change continuinity (continuous or not)
    }
    tracker++;
    if(tracker < 50) {
      return;
    }
    else {
      completion = true;
      digitalWrite(dirPiny, LOW);
      for(int g = 0; g<1; g++) {
        for (int i=0; i < stepsPerRevolution; i++){
          digitalWrite(stepPiny, HIGH);
          delayMicroseconds(500);
          digitalWrite(stepPiny, LOW);
          delayMicroseconds(500);
        }
        digitalWrite(stepPiny, LOW);
        digitalWrite(dirPinx, HIGH);
        //delay(500); // CHANGE THIS LINE to change continuinity (continuous or not)
      }
      digitalWrite(stepPinx, LOW);
      digitalWrite(stepPiny, LOW);
    } //3.356974 cm/sec
  }
  else {
    while(1);
  }
}
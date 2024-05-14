//Includes the Arduino Stepper Library
/**
#include <Stepper.h>

// Defines the number of steps per rotation
const int stepsPerRevolution = 2048;

// Creates an instance of stepper class
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
Stepper myStepper = Stepper(stepsPerRevolution, 8, 10, 9, 11);

void setup() {
    // Nothing to do (Stepper Library sets pins as outputs)
}

void loop() {
	// Rotate CW slowly at 5 RPM
	myStepper.setSpeed(5);
	myStepper.step(stepsPerRevolution);
	delay(1000);
	
	// Rotate CCW quickly at 10 RPM
	myStepper.setSpeed(10);
	myStepper.step(-stepsPerRevolution);
	delay(1000);
}
**/
//Code Explanation:
//The sketch starts by including the built-in stepper library.

//#include <Stepper.h>
//Next, a constant stepsPerRevolution is defined, which contains the number of ‘steps’ the motor takes to complete one revolution. In our case, it is 2038.


/**
const int stepsPerRevolution = 2038;
The step sequence of the 28BYJ-48 unipolar stepper motor is IN1-IN3-IN2-IN4. We will use this information to control the motor by creating an instance of the stepper library myStepper with the pin sequence 8, 10, 9, 11.

Make sure you do it right; otherwise, the motor won’t work properly.

Stepper myStepper = Stepper(stepsPerRevolution, 8, 10, 9, 11);
Since the stepper library internally configures the four control pins as outputs, there is nothing to configure in the setup function, so it is left empty.

Ezoic
void setup() {
}
In the loop function, we use the setSpeed() function to specify the speed at which the stepper motor should move and the step() function to specify how many steps to take.

Passing a negative number to the step() function causes the motor to spin in the opposite direction.

The first code snippet causes the motor to spin very slowly clockwise, while the second causes it to spin very quickly counter-clockwise.

Ezoic
void loop() {
	// Rotate CW slowly at 5 RPM
	myStepper.setSpeed(5);
	myStepper.step(stepsPerRevolution);
	delay(1000);
	
	// Rotate CCW quickly at 10 RPM
	myStepper.setSpeed(10);
	myStepper.step(-stepsPerRevolution);
	delay(1000);
}
Please keep in mind that step() is a blocking function. This means that the Arduino will wait until the motor stops running before proceeding to the next line in your sketch. For example, on a 100-step motor, if you set the speed to 1 RPM and call step(100), this function will take a full minute to finish.

Arduino Example Code 2 – Using AccelStepper library
The Arduino Stepper Library is perfect for simple, single-motor applications. However, if you want to control multiple steppers, you’ll need a more powerful library.

So, for our next experiment, we will use an advanced stepper motor library – the AccelStepper library. It outperforms the standard Arduino Stepper library in the following ways:

It supports acceleration and deceleration.
Ezoic
It supports half-step driving.
It supports multiple steppers at once, with independent concurrent stepping on each stepper.
This library is not included with the Arduino IDE, so you’ll need to install it first.

Ezoic
Library Installation
To install the library, navigate to Sketch > Include Library > Manage Libraries… Wait for the Library Manager to download the libraries index and update the list of installed libraries.

Manage Libraries
Filter your search by entering ‘accelstepper‘. Click on the first entry, and then choose Install.

Installing AccelStepper Library
Arduino Code
Here is a simple sketch that accelerates the stepper motor in one direction and then decelerates to come to rest. After one revolution, the motor reverses its spinning direction and repeats the process.

Ezoic
// Include the AccelStepper Library
#include <AccelStepper.h>

// Define step constant
#define MotorInterfaceType 4

// Creates an instance
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
AccelStepper myStepper(MotorInterfaceType, 8, 10, 9, 11);

void setup() {
	// set the maximum speed, acceleration factor,
	// initial speed and the target position
	myStepper.setMaxSpeed(1000.0);
	myStepper.setAcceleration(50.0);
	myStepper.setSpeed(200);
	myStepper.moveTo(2038);
}

void loop() {
	// Change direction once the motor reaches target position
	if (myStepper.distanceToGo() == 0) 
		myStepper.moveTo(-myStepper.currentPosition());

	// Move the motor one step
	myStepper.run();
}
Code Explanation:
The sketch begins by including the newly installed AccelStepper library.

#include <AccelStepper.h>
Following that, we specify the motor interface type for the AccelStepper library. In this case, we will be driving a four-wire stepper motor in full-step mode, so we set the MotorInterfaceType constant to 4. If you want to run the motor in half-step mode, set the constant to 8.

#define MotorInterfaceType 4
Next, we create an instance of the stepper library called myStepper with the appropriate motor interface type and a pin sequence of 8, 10, 9, 11. (Keep in mind that the step sequence for these motors is IN1-IN3-IN2-IN4).

Ezoic
AccelStepper myStepper(MotorInterfaceType, 8, 10, 9, 11);
In the setup function, the maximum permitted speed of the motor is set to 1000 (the motor will accelerate up to this speed when we run it). The acceleration/deceleration rate is then set to add acceleration and deceleration to the stepper motor’s movements.

The constant speed is set to 200. And, because the 28BYJ-48 takes 2038 steps per turn, the target position is also set to 2038.

void setup() {
	myStepper.setMaxSpeed(1000.0);
	myStepper.setAcceleration(50.0);
	myStepper.setSpeed(200);
	myStepper.moveTo(2038);
}
In the loop function, an if statement is used to determine how far the motor needs to travel (by reading the distanceToGo property) before reaching the target position (set by moveTo). When the distanceToGo reaches zero, the motor is rotated in the opposite direction by setting the moveTo position to negative of its current position.

Ezoic
At the bottom of the loop, you’ll notice that the run() function is called. This is the most important function, as the stepper will not move if it is not executed.

void loop() {
	// Change direction once the motor reaches target position
	if (myStepper.distanceToGo() == 0) 
		myStepper.moveTo(-myStepper.currentPosition());

	// Move the motor one step
	myStepper.run();
}
Arduino Example Code 3 – Control Two 28BYJ-48 Stepper Motors Simultaneously
In our next experiment, we will attempt to run two 28BYJ-48 stepper motors simultaneously.

Wiring
Let’s add a second 28BYJ-48 stepper motor to the setup.

Connect the ULN2003 driver’s VCC to 5V and GND to ground. Now connect IN1, IN2, IN3, and IN4 to Arduino digital pins 4, 5, 6, and 7 respectively.

The following table lists the pin connections:

ULN2003 Driver 1		Arduino
IN1	
8
IN2	
9
IN3	
10
IN4	
11
GND	
GND
ULN2003 Driver 2		Arduino
IN1	
4
IN2	
5
IN3	
6
IN4	
7
GND	
GND
The image below shows how to build the circuit.

Wiring Two 28BYJ48 Stepper Motors with Arduino
Arduino Code
Here’s a sketch that drives one motor in full-step mode and the other in half-step mode while accelerating and decelerating. After one revolution, their spinning direction changes.

// Include the AccelStepper Library
#include <AccelStepper.h>

// Define step constants
#define FULLSTEP 4
#define HALFSTEP 8

// Creates two instances
// Pins entered in sequence IN1-IN3-IN2-IN4 for proper step sequence
AccelStepper stepper1(HALFSTEP, 8, 10, 9, 11);
AccelStepper stepper2(FULLSTEP, 4, 6, 5, 7);

void setup() {
	// set the maximum speed, acceleration factor,
	// initial speed and the target position for motor 1
	stepper1.setMaxSpeed(1000.0);
	stepper1.setAcceleration(50.0);
	stepper1.setSpeed(200);
	stepper1.moveTo(2038);

	// set the same for motor 2
	stepper2.setMaxSpeed(1000.0);
	stepper2.setAcceleration(50.0);
	stepper2.setSpeed(200);
	stepper2.moveTo(-2038);
}

void loop() {
	// Change direction once the motor reaches target position
	if (stepper1.distanceToGo() == 0) 
		stepper1.moveTo(-stepper1.currentPosition());
	if (stepper2.distanceToGo() == 0) 
		stepper2.moveTo(-stepper2.currentPosition());

	// Move the motor one step
	stepper1.run();
	stepper2.run();
}
Code Explanation:
The sketch begins by including the AccelStepper library.

#include <AccelStepper.h>
As one motor will be driven in full-step mode and the other in half-step mode, the following two constants are defined.

#define FULLSTEP 4
#define HALFSTEP 8
Following that, two AccelStepper objects are created, one for each motor.

AccelStepper stepper1(HALFSTEP, 8, 10, 9, 11);
AccelStepper stepper2(FULLSTEP, 4, 6, 5, 7);
In the setup function, the maximum permitted speed for the first motor is set to 1000. The acceleration/deceleration rate is then set to add acceleration and deceleration to the stepper motor’s movements. The constant speed is set to 200. And, because the 28BYJ-48 takes 2038 steps per turn, the target position is set to 2038.

To make the second stepper motor rotate in the opposite direction, we followed the exact same procedure as for the first stepper motor, with the exception of setting the target position to -2038.

void setup() {
    // settings for motor 1
    stepper1.setMaxSpeed(1000.0);
    stepper1.setAcceleration(50.0);
    stepper1.setSpeed(200);
    stepper1.moveTo(2038);

    // settings for motor 2
    stepper2.setMaxSpeed(1000.0);
    stepper2.setAcceleration(50.0);
    stepper2.setSpeed(200);
    stepper2.moveTo(-2038);
}
In the loop function, two if statements are used, one for each motor, to determine how far the motors must travel (by reading the distanceToGo property) to reach their target position (set by moveTo). When the distanceToGo reaches zero, the motors are instructed to rotate in the opposite direction by setting their moveTo position to a negative value.

Finally, the run() function is called to get the motors spinning.

void loop() {
	// Change direction once the motor reaches target position
	if (stepper1.distanceToGo() == 0) 
		stepper1.moveTo(-stepper1.currentPosition());
	if (stepper2.distanceToGo() == 0) 
		stepper2.moveTo(-stepper2.currentPosition());

	// Move the motor one step
	stepper1.run();
	stepper2.run();
}
SHARE
Ezoic
DisclaimerPrivacy PolicyAboutContact Us
Copyright © 2024 LastMinuteEngineers.com. All rights reserved.
**/
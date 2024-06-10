#include <Stepper.h>

char Message[6]; // 6 char array to act as a buffer to store information from raspbery pi
char steps[2];// 4 char array to store all 

int x_pos;
int y_pos; // stores the x,y,z positions
int z_pos;

bool is_pos;

int steps_per_revolution = 2048;
// Pins entered in sequence  IN1 - IN3 - IN2 - IN4
Stepper stepper_x = Stepper(steps_per_revolution, 2, 4, 3, 5);
Stepper stepper_y = Stepper(steps_per_revolution, 10, 12, 11, 13);
Stepper stepper_z = Stepper(steps_per_revolution, 6, 8, 7, 9);


// char 1 -> specify x, y, z 
// char 2 -> specify direction, forward(1) and backward(0) 
// char 3-4 -> specify how many steps should be treated as string a full turn at a time 
// char 5-6 -> Currently unused

int buffToInteger(char* buffer)
{
    int a;
    memcpy( &a, buffer, sizeof( int ) );
    return a;
}

void send_all_good(){
  // send all done raspberry so can remove lock on send
  // or send position if is_pos is true 
  // should do stuff
  Serial.write(1);
}

void transcribe_message() {
  steps[0] = Message[2];
  steps[1] = Message[3];
  int to_move = buffToInteger(steps);
  if (Message[0] == 'x'){
    // To move in x-dimension
    //Serial.println("In x");
    move_x(to_move);
  }
  
  if (Message[0] == 'y'){
    // To move in y-dimension
    //Serial.println("In y");
    move_y(to_move);
  }
  if (Message[0] == 'z'){
    // To move in z-dimension
    //Serial.println("In z");
    move_z(to_move);
  }
  int to_wait = ((to_move/steps_per_revolution)*((60/5)*1000)) + 50; // gets how long to wait then adds 50ms
  delay(to_wait);
  }

void move_x(int to_move){
  bool direction;
  if (Message[1] == 1){
     //then move in forward direction
     stepper_x.setSpeed(5); // setting speed to 2.5 mm per minute (50 rpm)
     stepper_x.step(to_move);
  }
  else{
    // then move in backwards direction
    stepper_x.setSpeed(5); // setting speed to 2.5 mm per minute (50 rpm)
    stepper_x.step(-to_move);
  }
  // then wait until done 
}

void move_y(int to_move){
  bool direction;
  if (Message[1] == 1){
    // then move in forward direction
    stepper_y.setSpeed(5);
    stepper_y.step(to_move);
  }
  else{
    // then move in backwards direction
    stepper_y.setSpeed(5);
    stepper_y.step(-to_move);
  }
  // then wait until done 
}

void move_z(int to_move){
  bool direction;
  if (Message[1] == 1){
    // then move in forward direction
    stepper_z.setSpeed(5);
    stepper_z.step(to_move);
  }
  else{
    // then move in backwards direction
    stepper_z.setSpeed(5);
    stepper_z.step(-to_move);
  }
  // then wait until done 
}

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps (may have to change baudrate)
  while (!Serial){
    // Waits for serial to connect need to be connected via usb
  }
  
  stepper_x.setSpeed(5); // setting speed to 250 microns per minute (5 rpm)
  stepper_y.setSpeed(5); // setting speed to 250 microns per minute (5 rpm)
  stepper_z.setSpeed(5); // setting speed to 250 microns per minute (5 rpm)
  
}

void loop() {
  // send data only when you receive data:

  if (Serial.available() > 0) {
    // resets Message to 000000 before 
    //read the incoming bytes into message array
    int x = Serial.readBytes(Message, 6);
    transcribe_message();
    //steps[2] = Message[4];
    //steps[3] = Message[5];
    //Serial.println(x);
    //Serial.flush();
    send_all_good();
  }
}

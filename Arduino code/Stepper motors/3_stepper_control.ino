char Message[6]; // 6 char array to act as a buffer to store information from raspbery pi
char steps[4];// 4 char array to store all 

int x_pos;
int y_pos; // stores the x,y,z positions
int z_pos;

bool is_pos;

// char 1 -> specify x, y, z 
// char 2 -> specify direction, forward(1) and backward(0) 
// char 3-6 -> specify how many steps should be treated as string a full turn at a time 

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
}

void transcribe_message() {
if (Message[0] == 'x'){
  // To move in x-dimension
  move_x();
}
if (Message[0] == 'y'){
  // To move in y-dimension
  move_y();
}
if (Message[0] == 'z'){
  // To move in z-dimension
  move_z();
}
}

void move_x(){
  bool direction;
  if (Message[1] == '1'){
    // then move in forward direction
  }
  else{
    // then move in backwards direction
  }
  // then wait until done 
}

void move_y(){
  bool direction;
  if (Message[1] == '1'){
    // then move in forward direction
  }
  else{
    // then move in backwards direction
  }
  // then wait until done 
}

void move_z(){
  bool direction;
  if (Message[1] == '1'){
    // then move in forward direction
  }
  else{
    // then move in backwards direction
  }
  // then wait until done 
}

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps (may have to change baudrate)
  while (!Serial){
    // Waits for serial to connect need to be connected via usb
  }
}

void loop() {
  // send data only when you receive data:

  if (Serial.available() > 0) {
    // resets Message to 000000 before 
    Message[0] = 0;
    Message[1] = 0;
    Message[2] = 0;
    Message[3] = 0;
    Message[4] = 0;
    Message[5] = 0;
    steps[0] = 0;
    steps[1] = 0;
    steps[2] = 0;
    steps[3] = 0;
    //read the incoming bytes into message array
    int x = Serial.readBytes(Message, 6);
    //transcribe_message();
    steps[0] = Message[2];
    steps[1] = Message[3];
    steps[2] = Message[4];
    steps[3] = Message[5];
    int a = buffToInteger(steps);
    Serial.println(a);
    Serial.println(Message);
    Serial.flush();
    send_all_good();
  }
}
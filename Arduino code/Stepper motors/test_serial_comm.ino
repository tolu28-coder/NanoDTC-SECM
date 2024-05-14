/**int incomingByte = 0; // for incoming serial data
char incomingChar;
char Message[2];
int Ledpin = 8;

void read_message(int num_of_bytes=2) {
  int i = 0;
  while (Serial.available() > 0) {
    incomingChar = (char)Serial.read();
    Message[i] = incomingChar;
    i = i +1;
  }
}

void transcribe_message() {
if ((Message[0] == 'a') &&(Message[1] == 'b')) {
  digitalWrite(Ledpin, HIGH);
}
if ((Message[0] == 'b') &&(Message[1] == 'a')) {
  digitalWrite(Ledpin, LOW);
}
if (incomingChar == 'a'){
  digitalWrite(Ledpin, HIGH);
}
if (incomingChar == 'b'){
  digitalWrite(Ledpin, LOW);
}
}
**/
/**
void transcribe_message(char tmp) {
Serial.println(Message);
if (Message[0] == 'a' && Message[1] == 'b') {
  Serial.println("In High");
  digitalWrite(Ledpin, HIGH);
}
if ((Message[0] == 'b') &&(Message[1] == 'a')) {
  Serial.println("In Low");
  digitalWrite(Ledpin, LOW);
}

if (tmp == 'a'){
  digitalWrite(Ledpin, HIGH);
}
if (tmp == 'b'){
  digitalWrite(Ledpin, LOW);
}
}
void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  while (!Serial){
    // Waits for serial to connect need to be connected via usb
  }
  pinMode(Ledpin, OUTPUT);
}

void loop() {
  // send data only when you receive data:

  if (Serial.available() > 0) {
    Message[0] = 0;
    Message[1] = 0;
     //read the incoming byte:
    //incomingChar = (char)Serial.read();
    //read_message();
    //Serial.print(Message);
    //Serial.print(Message[1]);
    int x = Serial.readBytes(Message, 2);
    transcribe_message(incomingChar);
    //Serial.println("In High");
    Serial.flush();
    //digitalWrite(Ledpin, HIGH);
  }
}
**/




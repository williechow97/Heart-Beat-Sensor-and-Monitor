//Constants
const int irReceiver=A0; //IR Receiver is at Arduino analog pin A0
//Variables 
int value;              //Store value of IR Receiver
int i=0;

void setup() {
  Serial.begin(9600);
  pinMode(irReceiver, INPUT);  //Set irReceiver - A0 pin as an input 
}

void loop() {
  value=analogRead(irReceiver);
  Serial.println(value);
  //delay(50); //delay Arduino in milliseconds
}

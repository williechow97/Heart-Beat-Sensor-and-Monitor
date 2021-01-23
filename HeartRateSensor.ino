//Constants
const int irReceiver=A0; //IR Receiver is at Arduino analog pin A0
//Variables 
int value = 0;              //Store value of IR Receiver
unsigned long currentMicros;
unsigned long previousMicros=0;
unsigned long sampling_interval=40000;

void setup() {
  Serial.begin(9600);
  pinMode(irReceiver, INPUT);  //Set irReceiver - A0 pin as an input 
}

void loop() {
  currentMicros = micros();
  if(currentMicros-previousMicros >= sampling_interval){
    value=analogRead(irReceiver);  
    Serial.println(value);
    previousMicros = currentMicros;
  }
  //delay(50); //delay Arduino in milliseconds
}

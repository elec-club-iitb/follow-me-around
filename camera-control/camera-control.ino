#include <Servo.h>

Servo myservo;  // create servo object to control a servo

int currentval=90;
int val;    // variable to read the value from the analog pin

void setup() {
  Serial.begin(9600);
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  myservo.write(currentval); // sets the servo position according to the value
  delay(15);
  pinMode(10,OUTPUT);
  pinMode(11,OUTPUT);
  digitalWrite(10,HIGH);
  digitalWrite(11,LOW);
}

void loop() {
  if(Serial.available()){
    val = Serial.parseInt();             // read angle change value from serial
    currentval += val;                   // modify current angle
    myservo.write(currentval);           // sets the servo position according to the value
    delay(15);                           // waits for the servo to get there
    Serial.println(currentval);
  }
}


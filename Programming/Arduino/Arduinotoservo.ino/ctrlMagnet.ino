#include <Servo.h>

#define SERVO_PIN 3
#define CTRL_PIN 2

#define MAGNET_OFF -90
#define MAGNET_ON 270

Servo magnet;


void magnetON(bool on)
{
  magnet.write(on * MAGNET_ON + MAGNET_OFF);
}


void setup() {

  magnet.attach(3);
  pinMode(CTRL_PIN, INPUT);
}

bool ctrl_last = false;

void loop() {
  bool ctrl = digitalRead(CTRL_PIN);
  if (ctrl_last != ctrl)
  {
    magnetON(ctrl);
    ctrl_last = ctrl;
  }
  delay(50);
  
  
}

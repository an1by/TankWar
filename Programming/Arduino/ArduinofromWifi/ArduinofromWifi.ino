#include <SoftwareSerial.h>
#include <ArduinoJson.h>


#define LASER_PIN 2
#define LED_LIFE_PIN 3
#define LED_DEAD_PIN 4


#define RX_PIN 8
#define TX_PIN 9

SoftwareSerial UART(RX_PIN, TX_PIN);

StaticJsonDocument<JSON_OBJECT_SIZE(64)> json;

void setup() {

  pinMode(LED_PIN, OUTPUT);

  delay(1000);
  Serial.begin(115200);

  UART.begin(115200);

  
  Serial.println(F("---------START---------"));
}

void loop() {

  if (UART.available())
  {
    auto string_in = UART.readString();
    Serial.print(F("READ STRING="));
    Serial.println(string_in);
    if (string_in.startsWith(F("ERR")))
    {
      Serial.print(F("ERR="));
      Serial.println(string_in);
      return;
    }

    auto err = deserializeJson(json, string_in);
    if (err == DeserializationError::IncompleteInput)
    {
      err = deserializeJson(json, string_in + '}');
      Serial.println(err.f_str());
    }
    if (err)
    {
      Serial.print(F("ERR=deserializeJson()="));
      Serial.println(err.f_str());
      Serial.print(F("ERR=JSON="));
      Serial.println(string_in);
      return;
    }
    
    switch (json["action"])
      case "log_console":
        Serial.println(json["message"]);
      case "fire":
        digitalWrite(LASER_PIN, HIGH);
        delay(600);
        degitalWrite(LASER_PIN, LOW);
      case "status":
        digitalWrite(LED_LIFE, json["life"]);
        digitalWrite(LED_DEAD_PIN, !json["life"]);
  }
  
}

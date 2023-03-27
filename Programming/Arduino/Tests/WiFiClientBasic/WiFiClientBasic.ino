/*
    This sketch sends a string to a TCP server, and prints a one-line response.
    You must run a TCP server in your local network.
    For example, on Linux you can use this command: nc -v -l 3000

    16.3.2023
*/

#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ArduinoJson.h>

//#ifndef STASSID
//#define STASSID "Not Found"
//#define STAPSK "404404404"
//#endif

//const char* ssid = STASSID;
//const char* password = STAPSK;

#define LED_PIN D4

const char* host = "192.168.1.126";
const uint16_t port = 3030;

ESP8266WiFiMulti WiFiMulti;

template <int JSON_SIZE>
struct JSON
{
  StaticJsonDocument<JSON_OBJECT_SIZE(JSON_SIZE)> json;
  String string;

  void strUpdate()
  {
    serializeJson(json, string);
  }

  DeserializationError jsonUpdate()
  {
    return deserializeJson(json, string);
  }
};

JSON<3> json_out;
JSON<8> json_in;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  
  Serial.begin(115200);
  delay(1000);
	
	//FIX: Serial.read() не ждет
  Serial.print("SSID: ");     const char* ssid = "**********";//Serial.readStr5ing().c_str();
  Serial.print("\nPassword: "); const char* password = "********";//Serial.readString().c_str();
  // We start by connecting to a WiFi network
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(ssid, password);

  Serial.println();
  Serial.println();
  Serial.print("Wait for WiFi... ");

  while (WiFiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  json_out.json["command"] = "log";
  json_out.json["message"] = "LOLKEK";
  json_out.json["data"] = 0xABCD;

  json_out.strUpdate();
  Serial.println(json_out.string);

  delay(500);
}


void loop() {
  Serial.print("connecting to ");
  Serial.print(host);
  Serial.print(':');
  Serial.println(port);

  // Use WiFiClient class to create TCP connections
  static WiFiClient client;

  if (!client.connect(host, port)) {
    Serial.println("connection failed");
    Serial.println("wait 5 sec...");
    delay(5000);
    return;
  }

  // This will send the request to the server

  client.print(json_out.string);

  // read back one line from server
  Serial.println("receiving from remote server");
  json_in.string = client.readStringUntil('\r');
  DeserializationError err = json_in.jsonUpdate();

  if (!err)
  {
//    auto obj = json_in.json.as<JsonObject>();
//    for (JsonObject::iterator it=obj.begin(); it!=obj.end(); ++it) {
//      Serial.print(it->key().c_str()); // is a JsonString
//      Serial.print(":");
//      Serial.println(it->value()); // is a JsonVariant
//    }
    Serial.println(json_in.string);
    
    if (json_in.json["led"].as<bool>()) digitalWrite(LED_PIN, LOW );
    delay(json_in.json["time"].as<int>());
    digitalWrite(LED_PIN, HIGH); 
  }
  else
  {
    Serial.print("deserializeJson() failed with code ");
    Serial.println(err.f_str());
  }

  Serial.println("wait 5 sec...");
  delay(5000);
}

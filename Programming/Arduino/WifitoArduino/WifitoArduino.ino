 #include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>

const char* host = "play.aniby.net";
const uint16_t port = 3030;
const char* ssid = "Not Found";
const char* password = "404404404";

ESP8266WiFiMulti WiFiMulti;


void setup() {
  Serial.begin(115200);
  delay(1000);
	
	//FIX: Serial.read() не ждет
  //Serial.print("SSID: ");     //Serial.readString().c_str();
  //Serial.print("\nPassword: "); //Serial.readString().c_str();
  // We start by connecting to a WiFi network
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(ssid, password);

  // Serial.println();
  // Serial.println();
  // Serial.print("Wait for WiFi... ");

  while (WiFiMulti.run() != WL_CONNECTED) {
    Serial.println(F("ERR=NO_WL_CONNECTED"));
    delay(500);
  }

  delay(500);

}

void loop() {
  
  static WiFiClient client;

  if (!client.connected()) {
    client.connect(host, port);
    Serial.println(F("ERR:CONN_FAILED"));
    delay(5000);
    return;
  }

  if (client.available())
  {
    Serial.println(client.readStringUntil('\r'));
  }

}

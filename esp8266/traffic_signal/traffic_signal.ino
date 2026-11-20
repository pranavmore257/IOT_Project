/*
 * ESP8266 NodeMCU four-way traffic-signal controller.
 * Drives 12 LEDs through two cascaded 74HC595 shift registers and accepts
 * signal-state JSON from the laptop backend over MQTT.
 *
 * This is a tabletop educational prototype, not a controller for public roads.
 */
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// NodeMCU labels: D5=GPIO14 (clock), D6=GPIO12 (latch), D7=GPIO13 (data).
const uint8_t PIN_SR_CLOCK = D5;
const uint8_t PIN_SR_LATCH = D6;
const uint8_t PIN_SR_DATA = D7;

const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER = "192.168.1.100"; // Laptop IPv4 address on this Wi-Fi.
const uint16_t MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "ESP8266_Traffic_Signal";
const char* MQTT_USER = "";
const char* MQTT_PASSWORD = "";
const char* TOPIC_SIGNAL = "traffic/signal";
const char* TOPIC_STATUS = "traffic/status";

const unsigned long FAILSAFE_TIMEOUT_MS = 15000;
const unsigned long HEARTBEAT_INTERVAL_MS = 4000;

// Output bits: register 0 Q0..Q7 = N(R,Y,G), S(R,Y,G), E(R,Y);
// register 1 Q0..Q3 = E(G), W(R,Y,G). Bits Q4..Q7 remain unused/off.
enum SignalBit : uint8_t {
  NORTH_RED = 0, NORTH_YELLOW, NORTH_GREEN,
  SOUTH_RED, SOUTH_YELLOW, SOUTH_GREEN,
  EAST_RED, EAST_YELLOW, EAST_GREEN,
  WEST_RED, WEST_YELLOW, WEST_GREEN
};

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
uint16_t outputState = 0;
unsigned long lastSignalMessage = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastFailsafePhase = 0;
uint8_t failsafePhase = 0;
bool autonomousMode = false;

void writeOutputs() {
  digitalWrite(PIN_SR_LATCH, LOW);
  shiftOut(PIN_SR_DATA, PIN_SR_CLOCK, MSBFIRST, highByte(outputState));
  shiftOut(PIN_SR_DATA, PIN_SR_CLOCK, MSBFIRST, lowByte(outputState));
  digitalWrite(PIN_SR_LATCH, HIGH);
}

void setHead(uint8_t redBit, uint8_t yellowBit, uint8_t greenBit, const char* color) {
  outputState &= ~(static_cast<uint16_t>(1U << redBit) |
                   static_cast<uint16_t>(1U << yellowBit) |
                   static_cast<uint16_t>(1U << greenBit));
  if (strcmp(color, "GREEN") == 0) {
    outputState |= static_cast<uint16_t>(1U << greenBit);
  } else if (strcmp(color, "YELLOW") == 0) {
    outputState |= static_cast<uint16_t>(1U << yellowBit);
  } else {
    outputState |= static_cast<uint16_t>(1U << redBit);
  }
}

void applySignals(const char* north, const char* south, const char* east, const char* west) {
  setHead(NORTH_RED, NORTH_YELLOW, NORTH_GREEN, north);
  setHead(SOUTH_RED, SOUTH_YELLOW, SOUTH_GREEN, south);
  setHead(EAST_RED, EAST_YELLOW, EAST_GREEN, east);
  setHead(WEST_RED, WEST_YELLOW, WEST_GREEN, west);
  writeOutputs();
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  if (strcmp(topic, TOPIC_SIGNAL) != 0) return;

  StaticJsonDocument<512> doc;
  const DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
    Serial.printf("Invalid signal JSON: %s\n", error.f_str());
    return;
  }

  JsonObjectConst signals = doc["signals"].as<JsonObjectConst>();
  const char* north = signals["NORTH"] | "RED";
  const char* south = signals["SOUTH"] | "RED";
  const char* east = signals["EAST"] | "RED";
  const char* west = signals["WEST"] | "RED";
  const char* mode = doc["mode"] | "NORMAL";

  applySignals(north, south, east, west);
  autonomousMode = false;
  lastSignalMessage = millis();
  Serial.printf("Signal update (%s): N=%s S=%s E=%s W=%s\n",
                mode, north, south, east, west);
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.printf("Connecting to Wi-Fi %s", WIFI_SSID);
  const unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
    delay(250);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\nWi-Fi connected; IP=%s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\nWi-Fi unavailable; local failsafe will run.");
  }
}

void connectMqtt() {
  if (mqttClient.connected() || WiFi.status() != WL_CONNECTED) return;
  if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USER, MQTT_PASSWORD)) {
    mqttClient.subscribe(TOPIC_SIGNAL);
    Serial.println("MQTT connected; subscribed to traffic/signal.");
  }
}

void sendHeartbeat() {
  if (!mqttClient.connected()) return;
  StaticJsonDocument<192> doc;
  doc["device"] = "ESP8266_TRAFFIC_SIGNAL";
  doc["status"] = autonomousMode ? "AUTONOMOUS_FALLBACK" : "ONLINE_SLAVE";
  doc["ip"] = WiFi.localIP().toString();
  doc["rssi"] = WiFi.RSSI();
  doc["uptime_ms"] = millis();
  char payload[192];
  const size_t size = serializeJson(doc, payload, sizeof(payload));
  mqttClient.publish(TOPIC_STATUS, payload, size);
}

void runFailsafe() {
  const unsigned long now = millis();
  if (!autonomousMode) {
    autonomousMode = true;
    failsafePhase = 0;
    lastFailsafePhase = now;
  }

  // Each axis receives a fixed 6s green, 2s yellow and 1s all-red clearance.
  switch (failsafePhase) {
    case 0:
      applySignals("GREEN", "GREEN", "RED", "RED");
      lastFailsafePhase = now;
      failsafePhase = 1;
      break;
    case 1:
      if (now - lastFailsafePhase >= 6000) {
        applySignals("YELLOW", "YELLOW", "RED", "RED");
        lastFailsafePhase = now;
        failsafePhase = 2;
      }
      break;
    case 2:
      if (now - lastFailsafePhase >= 2000) {
        applySignals("RED", "RED", "RED", "RED");
        lastFailsafePhase = now;
        failsafePhase = 3;
      }
      break;
    case 3:
      if (now - lastFailsafePhase >= 1000) {
        applySignals("RED", "RED", "GREEN", "GREEN");
        lastFailsafePhase = now;
        failsafePhase = 4;
      }
      break;
    case 4:
      if (now - lastFailsafePhase >= 6000) {
        applySignals("RED", "RED", "YELLOW", "YELLOW");
        lastFailsafePhase = now;
        failsafePhase = 5;
      }
      break;
    case 5:
      if (now - lastFailsafePhase >= 2000) {
        applySignals("RED", "RED", "RED", "RED");
        lastFailsafePhase = now;
        failsafePhase = 0;
      }
      break;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SR_CLOCK, OUTPUT);
  pinMode(PIN_SR_LATCH, OUTPUT);
  pinMode(PIN_SR_DATA, OUTPUT);
  applySignals("RED", "RED", "RED", "RED");

  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(onMqttMessage);
  mqttClient.setBufferSize(512);
  connectWiFi();
  connectMqtt();
  lastSignalMessage = millis();
  lastFailsafePhase = millis();
  Serial.println("ESP8266 four-way signal controller ready.");
}

void loop() {
  connectWiFi();
  connectMqtt();
  mqttClient.loop();

  const unsigned long now = millis();
  if (now - lastHeartbeat >= HEARTBEAT_INTERVAL_MS) {
    sendHeartbeat();
    lastHeartbeat = now;
  }
  if (now - lastSignalMessage >= FAILSAFE_TIMEOUT_MS) {
    runFailsafe();
  } else {
    autonomousMode = false;
  }
  delay(10);
}
